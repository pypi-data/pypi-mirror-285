from __future__ import annotations
from .lib import (
    fzf,
    fzf_iter,
    FuzzyFinder,
    FuzzyFinderBuilder,
    FuzzyFinderOutput,
    SearchOptions,
    ResultsOptions,
    InterfaceOptions,
    Key,
    Event,
    ActionSimple,
    ActionWithArgType,
    ActionArgSeparator,
    ActionWithArg,
    Binding,
    LayoutType,
    BorderType,
    LabelPosition,
    LayoutOptions,
    BaseColorScheme,
    Color,
    DisplayOptions,
    HistoryOptions,
    PreviewOptions,
    ScriptingOptions,
)

import sys


def _tests():
    args = "\n".join(["aaaa asdas dasdasdad", "bbb asdasd badsds", "ccc asdkasnd"])

    basic = fzf(input_text=args)
    print(f"{basic=}")

    multi_iter = fzf_iter([33, 'aaa', BorderType.BLOCK], interface=InterfaceOptions(multi=True))
    print(f'{multi_iter=}')

    search = FuzzyFinderBuilder(search=SearchOptions(exact=True)).build().run(input_lines=args)
    print(f"{search=}")

    results = FuzzyFinderBuilder(results=ResultsOptions(tac=True)).build().run(input_lines=args)
    print(f"{results=}")

    multi = FuzzyFinderBuilder(interface=InterfaceOptions(multi=True)).build().run(input_lines=args)
    print(f"{multi=}")

    layout = FuzzyFinderBuilder(layout=LayoutOptions(border=BorderType.DOUBLE)).build().run(
        input_lines=args)
    print(f"{layout=}")

    display = FuzzyFinderBuilder(display=DisplayOptions(color=Color(
        base_scheme=BaseColorScheme.LIGHT_256))).build().run(input_lines=args)
    print(f"{display=}")

    history = FuzzyFinderBuilder(history=HistoryOptions(history_size=19)).build().run(
        input_lines=args)
    print(f"{history=}")

    preview = FuzzyFinderBuilder(preview=PreviewOptions(preview_label_pos=LabelPosition(
        offset=12))).build().run(input_lines=args)
    print(f"{preview=}")

    scripting = FuzzyFinderBuilder(scripting=ScriptingOptions(print0=True)).build().run(
        input_lines=args)
    print(f"{scripting=}")


def _go_nuts() -> None:
    binds = [
        Binding(binding=Event.ONE, actions=[ActionSimple.ACCEPT]),
        Binding(
            binding=Key.CTRL_R,
            actions=[
                ActionWithArg(
                    action_type=ActionWithArgType.CHANGE_PREVIEW_WINDOW,
                    argument="right,70%|top,60%",
                ),
                ActionWithArg(
                    action_type=ActionWithArgType.EXECUTE,
                    argument="notify-send {} -t 3000",
                    separator=ActionArgSeparator.PERCENT,
                ),
                ActionSimple.FIRST,
            ],
        )
    ]

    builder: FuzzyFinderBuilder = FuzzyFinderBuilder(
        search=SearchOptions(exact=True, case_sensitive=False),
        results=ResultsOptions(tac=True),
        interface=InterfaceOptions(multi=True, cycle=True, bind=binds),
        layout=LayoutOptions(layout=LayoutType.REVERSE, border=BorderType.SHARP, prompt="haha> "),
        display=DisplayOptions(ansi=True, color=Color(base_scheme=BaseColorScheme.LIGHT_256)),
        history=HistoryOptions(history_size=19),
        preview=PreviewOptions(preview_command="echo {} | tr [:lower:] [:upper:]"),
        scripting=ScriptingOptions(read0=True, print0=True),
    )
    fuzzy_finder: FuzzyFinder = builder.build()

    fzf_output: FuzzyFinderOutput = fuzzy_finder.run(input_lines="\0".join([
        "aaa a a a aaa a a a a a",
        "bb bw b f b bw b b bf db db  ",
        "cc case_sensitive c c       c c c ccccc",
        "asdasdasdas",
        "johnny",
        "",
        "asdasnkdaks",
    ]))

    print("fzf returned code:", fzf_output.exit_status_code)
    print("you picked:")
    for item in fzf_output.output:
        print('\t', item)


if __name__ == "__main__":
    _tests()
    _go_nuts()
