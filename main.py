from __future__ import annotations

import argparse

from simulation.runner import (
    run_first_tool_emergence_study,
    run_paper_data_capture,
    run_publication_batch_capture,
    run_robustness_sweep_capture,
    run_sexed_generation_test,
    run_sexed_world_body_search,
    run_visual_dashboard_demo,
    run_distinct_survivor_search,
    run_massive_lineage_search,
    run_prototype_experiment,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run artificial evolution experiments.")
    parser.add_argument(
        "--change-note",
        default="Manual test run",
        help="Describe what changed in this experiment run.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for the experiment.",
    )
    parser.add_argument(
        "--mode",
        choices=["prototype", "distinct-search", "massive-lineage", "dashboard", "paper", "publication-batch", "robustness-batch", "first-tool", "first-technology", "sexed-test", "sexed-search"],
        default="prototype",
        help="Run a prototype sweep, a distinct survivor search, a massive lineage search, a visual dashboard demo, or a research-grade paper capture.",
    )
    parser.add_argument(
        "--max-seed-rounds",
        type=int,
        default=50,
        help="Maximum number of seed rounds for distinct-search mode.",
    )
    parser.add_argument(
        "--max-stagnation-rounds",
        type=int,
        default=10,
        help="Stop distinct-search mode after this many seeds with no new body types.",
    )
    parser.add_argument(
        "--target-body-types",
        type=int,
        default=50,
        help="Target number of successful body types for search modes.",
    )
    parser.add_argument(
        "--dashboard-ticks",
        type=int,
        default=800,
        help="Maximum ticks for dashboard mode.",
    )
    parser.add_argument(
        "--snapshot-interval",
        type=int,
        default=10,
        help="Snapshot interval for dashboard replay output.",
    )
    parser.add_argument(
        "--paper-body-index",
        type=int,
        default=8,
        help="Candidate body index to use for paper mode.",
    )
    parser.add_argument(
        "--study-seeds",
        type=int,
        default=12,
        help="Number of seeds to run for first-tool study mode.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "distinct-search":
        run_distinct_survivor_search(
            start_seed=args.seed,
            change_note=args.change_note,
            target_body_types=args.target_body_types,
            max_seed_rounds=args.max_seed_rounds,
            max_stagnation_rounds=args.max_stagnation_rounds,
        )
    elif args.mode == "massive-lineage":
        run_massive_lineage_search(
            start_seed=args.seed,
            change_note=args.change_note,
            target_body_types=args.target_body_types,
            max_seed_rounds=args.max_seed_rounds,
        )
    elif args.mode == "dashboard":
        run_visual_dashboard_demo(
            seed=args.seed,
            change_note=args.change_note,
            max_ticks=args.dashboard_ticks,
            snapshot_interval=args.snapshot_interval,
        )
    elif args.mode == "paper":
        run_paper_data_capture(
            seed=args.seed,
            change_note=args.change_note,
            body_index=args.paper_body_index,
            max_ticks=args.dashboard_ticks,
            snapshot_interval=args.snapshot_interval,
        )
    elif args.mode == "publication-batch":
        run_publication_batch_capture(
            start_seed=args.seed,
            seed_count=args.study_seeds,
            change_note=args.change_note,
            max_ticks=args.dashboard_ticks,
            snapshot_interval=args.snapshot_interval,
        )
    elif args.mode == "robustness-batch":
        run_robustness_sweep_capture(
            start_seed=args.seed,
            seed_count=args.study_seeds,
            change_note=args.change_note,
            max_ticks=args.dashboard_ticks,
            snapshot_interval=args.snapshot_interval,
        )
    elif args.mode in {"first-tool", "first-technology"}:
        run_first_tool_emergence_study(
            start_seed=args.seed,
            seed_count=args.study_seeds,
            change_note=args.change_note,
            body_index=args.paper_body_index,
            max_ticks=args.dashboard_ticks,
        )
    elif args.mode == "sexed-test":
        run_sexed_generation_test(
            seed=args.seed,
            change_note=args.change_note,
            body_index=args.paper_body_index,
            max_ticks=args.dashboard_ticks,
        )
    elif args.mode == "sexed-search":
        run_sexed_world_body_search(
            start_seed=args.seed,
            change_note=args.change_note,
            max_ticks=args.dashboard_ticks,
            max_seed_rounds=min(args.max_seed_rounds, 3),
        )
    else:
        run_prototype_experiment(seed=args.seed, change_note=args.change_note)
