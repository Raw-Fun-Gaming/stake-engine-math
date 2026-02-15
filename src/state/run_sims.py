import asyncio
import cProfile
import random
import shutil
import time
from multiprocessing import Manager, Process
from typing import Dict
from warnings import warn

from src.writers.data import output_lookup_and_force_files


def create_books(
    game_state: object,
    config: object,
    num_sim_args: dict,
    batch_size: int,
    threads: int,
    compress: bool,
    profiling: bool,
):
    """Main run-function for simulating game outcomes and outputting all files."""
    for key, ns in num_sim_args.items():
        if all([ns > 0, ns > batch_size * batch_size]):
            assert (
                ns % (threads * batch_size) == 0
            ), "mode-sims/(batch * threads) must be divisible with no remainder"
        num_sim_args[key] = int(ns)

    if not compress and sum(num_sim_args.values()) > 1e4:
        warn("Generating large number of uncompressed books!")

    if profiling and threads > 1:
        raise RuntimeError(
            "Multithread profiling not supported, threads must = 1 with profiling enabled"
        )

    startTime = time.time()
    print("\nCreating books...")
    for bet_mode_name in num_sim_args:
        if num_sim_args[bet_mode_name] > 0:
            game_state.bet_mode = bet_mode_name
            run_multi_process_sims(
                threads,
                batch_size,
                config.game_id,
                bet_mode_name,
                game_state,
                num_sims=num_sim_args[bet_mode_name],
                compress=compress,
                write_event_list=config.write_event_list,
                profiling=profiling,
            )
            output_lookup_and_force_files(
                threads,
                batch_size,
                config.game_id,
                bet_mode_name,
                game_state,
                num_sims=num_sim_args[bet_mode_name],
                compress=compress,
            )  # , write_event_list=config.write_event_list)
    shutil.rmtree(game_state.output_files.temp_path)
    print("\nFinished creating books in", time.time() - startTime, "seconds.\n")


def get_sim_splits(
    game_state: object, num_sims: int, bet_mode_name: str
) -> Dict[str, int]:
    """Ensure assignment of criteria to all simulations numbers."""
    bet_mode_distributions = game_state.get_bet_mode(bet_mode_name).get_distributions()
    num_sims_criteria = {
        d._criteria: max(int(num_sims * d._quota), 1) for d in bet_mode_distributions
    }
    total_sims = sum(num_sims_criteria.values())
    reduce_sims = total_sims > num_sims
    listedCriteria = [d._criteria for d in bet_mode_distributions]
    criteria_weights = [d._quota for d in bet_mode_distributions]
    random.seed(0)
    while sum(num_sims_criteria.values()) != num_sims:
        c = random.choices(listedCriteria, criteria_weights)[0]
        if reduce_sims and num_sims_criteria[c] > 1:
            num_sims_criteria[c] -= 1
        elif not reduce_sims:
            num_sims_criteria[c] += 1

    return num_sims_criteria


def assign_sim_criteria(num_sims_criteria: Dict[str, int], sims: int) -> Dict[int, str]:
    """Assign criteria randomly to simulations based on quota defined in config."""
    simAllocation = [
        criteria for criteria, count in num_sims_criteria.items() for _ in range(count)
    ]
    random.shuffle(simAllocation)
    return {i: simAllocation[i] for i in range(min(sims, len(simAllocation)))}


async def profile_and_visualize(
    game_id,
    game_state,
    all_bet_mode_configs,
    bet_mode,
    sim_allocation,
    threads,
    num_repeats,
    sims_per_thread,
    repeat,
    compress,
    write_event_list,
):
    """Create flame-graph, automatically opens output on localhost."""
    output_string = f"games/{game_id}/simulationProfile_{bet_mode}.prof"
    cProfile.runctx(
        "game_state.run_sims(all_bet_mode_configs, bet_mode, sim_allocation, threads, num_repeats, sims_per_thread, 0, repeat, compress, write_event_list)",
        globals(),
        locals(),
        output_string,
    )
    await asyncio.create_subprocess_exec("snakeviz", output_string)


def run_multi_process_sims(
    threads: int,
    batching_size: int,
    game_id: str,
    bet_mode: str,
    game_state: object,
    num_sims: int = 1000000,
    compress: bool = True,
    write_event_list: bool = False,
    profiling: bool = False,
):
    """Setup multiprocessing manager for running all game-mode simulations."""
    print("\nCreating books for", game_id, "in", bet_mode)
    num_repeats = max(int(round(num_sims / threads / batching_size, 0)), 1)
    sims_per_thread = int(num_sims / threads / num_repeats)
    num_sims_criteria = get_sim_splits(game_state, num_sims, bet_mode)
    sim_allocation = assign_sim_criteria(num_sims_criteria, num_sims)
    for repeat in range(num_repeats):
        print("Batch", repeat + 1, "of", num_repeats)
        processes = []
        manager = Manager()
        all_bet_mode_configs = manager.list()
        if profiling:
            asyncio.run(
                profile_and_visualize(
                    game_id=game_id,
                    game_state=game_state,
                    all_bet_mode_configs=all_bet_mode_configs,
                    bet_mode=bet_mode,
                    sim_allocation=sim_allocation,
                    threads=threads,
                    num_repeats=num_repeats,
                    sims_per_thread=sims_per_thread,
                    repeat=repeat,
                    compress=compress,
                    write_event_list=write_event_list,
                )
            )
        elif threads == 1:
            game_state.run_sims(
                all_bet_mode_configs,
                bet_mode,
                sim_allocation,
                threads,
                num_repeats,
                sims_per_thread,
                0,
                repeat,
                compress,
                write_event_list,
            )
        else:
            for thread in range(threads):
                process = Process(
                    target=game_state.run_sims,
                    args=(
                        all_bet_mode_configs,
                        bet_mode,
                        sim_allocation,
                        threads,
                        num_repeats,
                        sims_per_thread,
                        thread,
                        repeat,
                        compress,
                        write_event_list,
                    ),
                )
                print("Started thread", thread)
                process.start()
                processes += [process]
            print("All threads are online.")
            for process in processes:
                process.join()
            print("Finished joining threads.")
            game_state.combine(all_bet_mode_configs, bet_mode)
            game_state.get_bet_mode(bet_mode).lock_force_keys()
