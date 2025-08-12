use std::rc::Rc;

// #![deny(warnings)]
use anyhow::{self, Context};
use clap::Parser;
use smol::LocalExecutor;
use tracing::{debug, info};
use tracing_subscriber::filter::EnvFilter;
use tracing_subscriber::{fmt, prelude::*};
use trustworthiness_checker::cli::adapters::DistributionModeBuilder;
use trustworthiness_checker::core::{AbstractMonitorBuilder, Runnable};
use trustworthiness_checker::dep_manage::interface::{DependencyKind, create_dependency_manager};
use trustworthiness_checker::io::InputProviderBuilder;
use trustworthiness_checker::io::builders::OutputHandlerBuilder;
use trustworthiness_checker::runtime::RuntimeBuilder;
use trustworthiness_checker::runtime::builder::DistributionMode;
use trustworthiness_checker::semantics::distributed::localisation::Localisable;
use trustworthiness_checker::{self as tc, io::file::parse_file};

use macro_rules_attribute::apply;
use smol_macros::main as smol_main;
use trustworthiness_checker::cli::args::{Cli, Language, ParserMode};

#[global_allocator]
static GLOBAL: jemallocator::Jemalloc = jemallocator::Jemalloc;

#[apply(smol_main)]
async fn main(executor: Rc<LocalExecutor<'static>>) -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(fmt::layer().with_writer(std::io::stderr))
        // Uncomment the following line to enable full span events which logs
        // every time the code enters/exits an instrumented function/block
        // .with(fmt::layer().with_span_events(FmtSpan::FULL))
        .with(EnvFilter::from_default_env())
        .init();

    let cli = Cli::parse();

    let builder = RuntimeBuilder::new();

    let parser = cli.parser_mode.unwrap_or(ParserMode::Combinator);
    let language = cli.language.unwrap_or(Language::DynSRV);

    let mqtt_port = cli.mqtt_port;
    let redis_port = cli.redis_port;
    let redis_host = cli.redis_host.clone();

    let builder = builder.executor(executor.clone());

    let builder = builder.maybe_semantics(cli.semantics);

    let builder = builder.maybe_runtime(cli.runtime);

    let model_parser = match language {
        Language::DynSRV => tc::lang::dynamic_lola::parser::lola_specification,
        Language::Lola => tc::lang::dynamic_lola::parser::lola_specification,
    };

    let builder = builder.scheduler_mode(cli.scheduling_mode.clone());

    debug!("Choosing distribution mode");
    let distribution_mode_builder = DistributionModeBuilder::new(cli.distribution_mode)
        .maybe_local_node(cli.local_node)
        .maybe_dist_constraints(cli.distribution_constraints);
    let builder = builder.distribution_mode_builder(distribution_mode_builder);

    let model = match parser {
        ParserMode::Combinator => parse_file(model_parser, cli.model.as_str())
            .await
            .context("Model file could not be parsed")?,
        ParserMode::Lalr => anyhow::bail!("LALR parser not currently implemented"),
    };
    info!(?model, output_vars=?model.output_vars, input_vars=?model.input_vars, "Parsed model");

    // Localise the model to contain only the local variables (if needed)
    let model = if let DistributionMode::LocalMonitor(locality_mode) = &builder.distribution_mode {
        let model = model.localise(locality_mode);
        info!(name: "Localised model", ?model, output_vars=?model.output_vars, input_vars=?model.input_vars);
        model
    } else {
        model
    };

    // Create the dependency manager
    let builder = builder.dependencies(create_dependency_manager(
        DependencyKind::DepGraph,
        model.clone(),
    ));

    let output_var_names = model.output_vars.clone();
    let builder = builder.model(model.clone());

    // Create the input provider builder
    let input_provider_builder = InputProviderBuilder::new(cli.input_mode)
        .executor(executor.clone())
        .model(model)
        .lang(language)
        .mqtt_port(mqtt_port)
        .redis_port(redis_port)
        .redis_host(redis_host.clone());
    let builder = builder.input_provider_builder(input_provider_builder);

    // Create the output handler
    let output_handler_builder = OutputHandlerBuilder::new(cli.output_mode)
        .executor(executor.clone())
        .output_var_names(output_var_names)
        .mqtt_port(mqtt_port)
        .redis_port(redis_port)
        .redis_host(redis_host);

    let builder = builder.output_handler_builder(output_handler_builder);

    // Create the runtime
    let monitor = builder.async_build().await;

    monitor.run().await
}
