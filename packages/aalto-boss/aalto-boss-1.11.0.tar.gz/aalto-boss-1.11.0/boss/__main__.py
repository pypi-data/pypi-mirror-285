import sys

from boss import __version__
from boss.bo.bo_main import BOMain
from boss.settings import Settings
from boss.io.main_output import MainOutput
from boss.mep.mepmain import MEPMain
from boss.pp.pp_main import PPMain
from boss.utils.timer import Timer
from boss.io.parse import parse_input_file
from boss.pp.pf_main import PFMain


def main(args=None):
    """The main routine."""
    # start timers
    local_timer = Timer()

    if args is None:
        args = sys.argv[1:]

    if not args_ok(args):  # Exit immediately if one or more args are invalid.
        print(
            "BOSS version "
            + str(__version__)
            + "\n"
            + "Usage:\n"
            + "   boss op <inputfile or rst-file>\n"
            + "   boss o <inputfile or rst-file>\n"
            + "   boss p <rst-file> <out-file>\n"
            + "   boss m <rst-file> <minima-file>\n"
            + "See the documentation for further instructions."
        )
        return

    if not files_ok(args[1:]):  # Exit immediately if input file doesn't open.
        return

    input_data = parse_input_file(args[1])
    settings = Settings(input_data["keywords"])

    # Don't overwrite an optimization run's outfile.
    if len(args) == 3:
        ipt_outfile = args[2]
        if "m" in args[0]:
            settings["outfile"] = settings["outfile"][:-4] + "_mep.out"
        else:
            settings["outfile"] = settings["outfile"][:-4] + "_pp.out"

    main_output = None

    # 1. Run bayesian optimization. Note: if we run an optimization we let BOMain
    # handle the MainOutput
    if "o" in args[0] and (settings["initpts"] + settings["iterpts"]) > 0:
        local_timer.startLap()

        rst_data = input_data.get("rst_data", None)
        bo = BOMain.from_settings(settings, rst_data)
        main_output = bo.main_output
        bo.run()

        main_output.progress_msg(
            "| Bayesian optimization completed, "
            + "time [s] %s" % (local_timer.str_lapTime()),
            True,
            True,
        )

    # If no optmization was run, we need to initialize the MainOutput and
    # start a new file manually
    if not main_output:
        main_output = MainOutput(settings)
        main_output.new_file()

    # 2. Run post-processing.
    if "p" in args[0]:
        local_timer.startLap()
        main_output.progress_msg("Starting post-processing...", True)
        main_output.section_header("POST-PROCESSING")

        ipt_rstfile = settings["rstfile"] if "o" in args[0] else args[1]
        if len(args) != 3:
            ipt_outfile = settings["outfile"]

        settings["rstfile"] = ipt_rstfile
        settings["outfile"] = ipt_outfile

        pp_main = PPMain.from_file(ipt_rstfile, ipt_outfile, main_output=main_output)
        pp_main.run()

        main_output.progress_msg(
            "Post-processing completed, " + "time [s] %s" % (local_timer.str_lapTime()),
        )

    # 3. Find minimum energy paths.
    if "m" == args[0]:
        local_timer.startLap()
        main_output.progress_msg("Finding minimum energy paths...", True)
        main_output.section_header("MINIMUM ENERGY PATHS")

        MEPMain(settings, args[1], args[2], main_output)
        main_output.progress_msg(
            "Finding minimum energy paths completed, "
            + "time [s] %s" % (local_timer.str_lapTime()),
        )

    main_output.footer(local_timer.str_totalTime())

    # 4. Pareto Front calculations
    if "f" == args[0]:
        from numpy import shape

        print("Pareto calculations will start for files %s" % (args[1:]))

        def dummy():
            pass

        def rst_files_for_pf(*args):
            files = args[0][1:]  # ["boss1.rst", "boss2.rst"]
            num_tasks = shape(files)[0]
            all_models = [BOMain.from_file(files[i], f=dummy) for i in range(num_tasks)]
            run_models = [all_models[i].run() for i in range(num_tasks)]
            pf_mesh = run_models[0].settings["pf_mesh"]
            pf_models = [PFMain(models=all_models[i].model) for i in range(num_tasks)]
            bounds = all_models[0].bounds
            initpts = [shape(run_models[i].select("X"))[0] for i in range(num_tasks)]
            return num_tasks, initpts, bounds, pf_models, pf_mesh

        num_tasks, initpts, bounds, pf_models, pf_mesh = rst_files_for_pf(args)

        def pf_multi_model():
            bo_MO = BOMain(
                [*[pf_models[i].boss_functions() for i in range(num_tasks)]],
                bounds=bounds,
                num_tasks=num_tasks,
                iterpts=0,
                task_initpts=initpts,
            )
            bo_MO.run()
            return bo_MO

        # calculate pareto fronts and optimal solutions
        bo_MO = pf_multi_model()
        pf = PFMain(n_tasks=num_tasks, bounds=bounds, mesh_size=pf_mesh, models=bo_MO)
        pf.run()
        # Visualise
        pf.plot_pos()
        pf.plot_pf()


def args_ok(args):
    """
    Checks that the user has called BOSS properly by examining the arguments
    given, number of files and filename extensions. BOSS should be called with
    one of the following:
        boss o options/.rst-file
        boss op options/.rst-file
        boss p .rst-file .out-file
        boss m .rst-file local_minima.dat
    """
    # TODO prevent calling boss pm
    some_args = len(args) > 0
    if some_args:
        optim_ok = "o" in args[0] and len(args) == 2
        justpp_arg_ok = "o" not in args[0] and "p" in args[0] and len(args) == 3
        mep_arg_ok = "o" not in args[0] and "m" in args[0] and len(args) == 3
        rst_incl = len(args) >= 2 and ".rst" in args[1]
        out_incl = len(args) == 3 and ".out" in args[2]
        dat_incl = len(args) == 3 and ".dat" in args[2]
        justpp_ok = justpp_arg_ok and rst_incl and out_incl
        mep_ok = mep_arg_ok and rst_incl and dat_incl
        pareto_ok = "f" in args[0]
    return some_args and (optim_ok or justpp_ok or mep_ok or pareto_ok)


def files_ok(filenames):
    """
    Checks that the given files exist and can be opened.
    """
    for fname in filenames:
        try:
            f = open(fname, "r")
            f.close()
        except FileNotFoundError:
            print("Could not find file '" + fname + "'")
            return False
    return True


# Start BOSS
if __name__ == "__main__":
    main()
