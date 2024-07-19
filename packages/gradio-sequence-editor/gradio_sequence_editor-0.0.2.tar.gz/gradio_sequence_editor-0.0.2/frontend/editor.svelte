<svelte:options accessors={true} />

<script lang="ts">
    import { onMount } from "svelte";
    import type { Gradio } from "@gradio/utils";
    import type { LoadingStatus } from "@gradio/statustracker";
    import SequenceInput from "./sequence-input.svelte";
    import {
        AcidAttrMap,
        Bulkiness,
        HydrophobicityIndex,
        Polarity,
        calcSequencePl,
        calcSequenceWeight,
        calcTotalHydrophobicity,
        pKa,
    } from "./utils/sequence";
    import { getSequenceColor } from "./utils/color";
    import { downloadAsText, guid } from "./utils/string";
    import { RcsbFv } from "@rcsb/rcsb-saguaro";
    import MenuSurface from "@smui/menu-surface";
    import List, { Item, Separator, Text } from "@smui/list";
    import {
        Button,
        Dropdown,
        DropdownItem,
        Tabs,
        TabItem,
        Tooltip,
        Input,
        Modal,
        Table,
        TableHead,
        TableHeadCell,
        TableBody,
        TableBodyCell,
        TableBodyRow,
    } from "flowbite-svelte";
    import fileSelector from "./utils/fileSelector";

    export let gradio: Gradio<{
        change: never;
        submit: never;
        input: never;
        clear_status: LoadingStatus;
    }>;
    export let value;
    export let initSequences;

    const guid = () => {
        function S4() {
            // eslint-disable-next-line no-bitwise
            return (((1 + Math.random()) * 0x10000) | 0)
                .toString(16)
                .substring(1);
        }
        return `${S4() + S4()}-${S4()}-${S4()}-${S4()}-${S4()}${S4()}${S4()}`;
    };
    const key = guid();
    $: key;

    const boardConfig = {
        trackWidth: 360,
        rowTitleWidth: 100,
        includeAxis: false,
        displayColor: "#48b596",
        titleFlagColor: "#000000",
        hideRowGlow: true,
        minRatio: 0,
    };
    window.process = {
        env: {
            NODE_ENV: "production",
            LANG: "",
        },
    };

    let el: HTMLTextAreaElement | HTMLInputElement;
    const container = true;

    function handle_change(): void {
        gradio.dispatch("change");
    }

    // When the value changes, dispatch the change event via handle_change()
    // See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive
    $: value, handle_change();

    let saguaroRef;

    let sequences = [];
    let undoList = [];
    let redoList = [];
    let inputSequenceModalVisible = false;
    let colorByResidue = true;
    let conservedResidue = false;
    let sequenceProps;
    let currSelection = {
        begin: -1,
        end: -1,
    };
    let active = "edit";
    let activeSequenceId = "";
    let activeSequenceIdx;
    let deleteModalVisible = false;
    let currSequence = [];
    let currName = "";
    let viewResidueSequenceId;
    $: sequences, syncSequenceProps();
    $: activeSequence = sequences.find((item) => item.id === activeSequenceId);
    $: selectionSequences =
        currSelection.begin !== -1
            ? sequences.map((item) =>
                  item.sequence.slice(
                      currSelection.begin - 1,
                      currSelection.end,
                  ),
              )
            : new Array(sequences.length);
    $: sequences, syncCurrSequence();
    $: residuePropsTableData =
        sequences
            .find((item) => item.id === viewResidueSequenceId)
            ?.sequence.split("")
            .map((residue, index) => ({
                pos: index + 1,
                residue,
                name: AcidAttrMap.get(residue) || "",
                index: index + 1,
                uid: index + 1,
                pKa: pKa[residue] ?? "",
                polarity: Polarity[residue] ?? "",
                bulkiness: Bulkiness[residue] ?? "",
                hyd: HydrophobicityIndex[residue] ?? "",
            })) ?? [];
    const syncCurrSequence = () => {
        value = sequences;
        currSequence = sequences.map((item) => item.sequence);
    };
    const updateSequences = (data) => {
        undoList = [...undoList, sequences].slice(undoList.length + 1 - 20);
        if (redoList.length) {
            redoList = [];
        }
        sequences = data;
    };
    const undo = () => {
        if (!undoList.length) {
            return;
        }
        redoList = [...redoList, sequences].slice(
            redoList.length + 1 > 20 ? redoList.length + 1 - 20 : 0,
        );
        updateSequencesConfig(undoList[undoList.length - 1]);
        undoList = undoList.slice(0, -1);
    };
    const redo = () => {
        if (!redoList.length) {
            return;
        }
        undoList = [...undoList, sequences].slice(
            undoList.length + 1 > 20 ? undoList.length + 1 - 20 : 0,
        );
        updateSequencesConfig(redoList[redoList.length - 1]);
        redoList = redoList.slice(0, -1);
    };

    const syncSequenceProps = () => {
        sequenceProps = sequences.map((item) => ({
            chainId: item.name,
            length: item.sequence.length,
            hydrophobicity: calcTotalHydrophobicity(item.sequence),
            kDa: calcSequenceWeight(item.sequence),
            pl: calcSequencePl(item.sequence),
        }));
        if (!sequences.length) return;
        if (!activeSequenceId) activeSequenceId = sequences[0].id;
        if (!activeSequenceIdx) activeSequenceIdx = 0;
        if (!currName) currName = sequences[0].name;
        if (!viewResidueSequenceId) viewResidueSequenceId = sequences[0].id;
    };
    const getDisplayConfig = (sequence: string, conservedSequence?: string) => {
        return sequence.split("").map((residue: string, idx: number) => ({
            displayType: "sequence",
            displayColor:
                conservedSequence?.[idx] !== residue && colorByResidue
                    ? getSequenceColor(residue)
                    : "#000000",
            displayId: guid(),
            displayData: [
                {
                    begin: idx + 1,
                    label: conservedSequence?.[idx] !== residue ? residue : "*",
                },
            ],
        }));
    };
    const updateSequencesConfig = (newData, isUndoRedo = true) => {
        saguaroRef?.updateBoardConfig({
            boardConfigData: {
                ...boardConfig,
                includeAxis: !!newData.length,
                range: {
                    min: 1,
                    max: Math.max(
                        ...newData.map((item) => item.sequence.length),
                    ),
                },
            },
            rowConfigData: newData.map((item, idx) => ({
                trackId: item.id,
                trackHeight: 24,
                trackColor: "#F9F9F9",
                displayConfig: getDisplayConfig(
                    item.sequence,
                    idx !== 0 && conservedResidue
                        ? newData[0].sequence
                        : undefined,
                ),

                displayType: "composite",
                rowTitle: {
                    visibleTex: item.name || "SEQUENCE",
                    style: {
                        color: '#ffffff'
                    },
                },
                // rowPrefix: <div>123</div>,
                nonEmptyDisplay: true,
                minRatio: 0,
                // 检查选中状态 saguaroRef?.rcsbFvStateManager.selection.selectedElements
                // 判断右键 e.button === 2
                elementClickCallback: (d: any, e: any) => {
                    currSelection = d ?? {
                        begin: -1,
                        end: -1,
                    };
                },
                titleFlagColor: "transparent",
            })),
        });
        if (!sequences.length) {
            setTimeout(() => {
                saguaroRef?.setDomain([
                    -0.5,
                    Math.ceil((boardConfig.trackWidth / 360) * 20) + 0.5,
                ]);
            }, 100);
        }
        if (!isUndoRedo) {
            updateSequences(newData);
        } else {
            sequences = newData;
        }
    };
    const setSequence = (sequence: string) => {
        const lines = sequence.split(/\n|\r/g);
        const result: any[] = [];
        let current = {
            name: "",
            sequence: "",
            id: guid(),
        };
        lines.forEach((line) => {
            if (line.startsWith(">")) {
                const name = line.slice(1);
                if (current.sequence) {
                    result.push({ ...current });
                }
                current = {
                    name,
                    sequence: "",
                    id: guid(),
                };
            } else {
                current.sequence += line.trim();
            }
        });
        if (current.sequence) {
            result.push({ ...current });
        }
        if (!result.length) return;
        const res = [...sequences, ...result] as {
            name: string;
            sequence: string;
            id: string;
        }[];
        // TODO 也要进Undo
        updateSequencesConfig(res, false);
    };
    const exportSequences = () => {
        const res = sequences
            .map((item) => `> ${item.name}\n\n${item.sequence.trim()}`)
            .join("\n\n");
        downloadAsText("App.fasta", res);
    };
    const setSequenceColor = (value = true) => {
        saguaroRef?.updateBoardConfig({
            boardConfigData: saguaroRef?.boardConfigData,
            rowConfigData: saguaroRef?.boardDataSate.rowConfigData.map(
                (item: any) => ({
                    ...item,
                    displayConfig: item.displayConfig?.map((item: any) => ({
                        ...item,
                        displayColor: value
                            ? getSequenceColor(item.displayData[0].label)
                            : "#000000",
                    })),
                }),
            ),
        });
        colorByResidue = value;
    };
    const changeConservedResidue = () => {
        const newState = !conservedResidue;
        saguaroRef?.updateBoardConfig({
            boardConfigData: {
                ...boardConfig,
                includeAxis: !!sequences.length,
                range: {
                    min: 1,
                    max: Math.max(
                        ...sequences.map((item) => item.sequence.length),
                    ),
                },
            },
            rowConfigData: sequences.map((item, idx) => ({
                trackId: item.id,
                trackHeight: 24,
                trackColor: "#F9F9F9",
                displayConfig: getDisplayConfig(
                    item.sequence,
                    idx !== 0 && newState ? sequences[0].sequence : undefined,
                ),

                displayType: "composite",
                rowTitle: item.name || "SEQUENCE",
                nonEmptyDisplay: true,
                minRatio: 0,
                // 检查选中状态 saguaroRef?.rcsbFvStateManager.selection.selectedElements
                // 判断右键 e.button === 2
                elementClickCallback: (d: any, e: any) => {
                    currSelection = d ?? {
                        begin: -1,
                        end: -1,
                    };
                },
            })),
        });
        conservedResidue = newState;
    };
    const importFasta = async () => {
        fileSelector.setAttrs({ accept: `.fasta` });
        const fileList = await fileSelector.selectFile();
        const file = fileList.item(0);
        if (!file) return;
        const sequence = await file.text();
        setSequence(sequence);
    };
    onMount(() => {
        const container = document.getElementById(`saguaro-container-${key}`);
        if (container?.clientWidth) {
            boardConfig.trackWidth = container?.clientWidth - 150;
        }
        saguaroRef = new RcsbFv({
            boardConfigData: {
                ...boardConfig,
            },
            rowConfigData: [],
            elementId: "htmlElementId",
        });
        if (initSequences) {
            setTimeout(() => {
                setSequence(initSequences);
            }, 100);
        }
    });
    const updateSequence = () => {
        if (saguaroRef) {
            setSequence(initSequences);
        }
    };
    $:initSequences, updateSequence();
</script>

<div id="saguaro-container-{key}" class="saguaro-container">
    <div style="display: {sequences?.length ? 'none' : 'block'}">
        <SequenceInput
            {gradio}
            submit={(seq) => {
                setSequence(seq);
            }}
        />
    </div>
    <div style="display: {!sequences.length ? 'none' : 'block'}">
        <div
            class="row"
            style="justify-content: start;align-items: center;margin-bottom: 12px;"
        >
            <Button
                color="light"
                style="padding: 0.625rem 1.25rem !important;margin-right: 16px"
                class="dark:bg-gray-800">Add</Button
            >
            <Dropdown>
                <DropdownItem
                    on:click={() => {
                        importFasta();
                    }}>Import .fasta</DropdownItem
                >
                <DropdownItem
                    on:click={() => {
                        inputSequenceModalVisible = true;
                    }}>Input Sequence</DropdownItem
                >
            </Dropdown>
            <Button
                color="light"
                on:click={undo}
                disabled={!undoList.length}
                style="padding: 0.625rem 1.25rem !important;margin-right: 16px"
            >
                Undo
            </Button>
            <Button
                color="light"
                on:click={redo}
                disabled={!redoList.length}
                style="padding: 0.625rem 1.25rem !important;margin-right: 16px"
            >
                Redo
            </Button>
            <Button
                color="light"
                on:click={exportSequences}
                disabled={!sequences.length}
                style="padding: 0.625rem 1.25rem !important;margin-right: 16px"
            >
                Export
            </Button>
        </div>
        <div class="row" style="justify-content: start;align-items: center;">
            <Button
                color="light"
                on:click={() => {
                    setSequenceColor(!colorByResidue);
                }}
                style="padding: 0.625rem 1.25rem !important;margin-right: 16px;"
            >
                Color Mode({colorByResidue ? "Open" : "Close"})
            </Button>
            <Button
                color="light"
                on:click={() => {
                    changeConservedResidue();
                }}
                style="padding: 0.625rem 1.25rem !important;margin-right: 16px"
            >
                Display conserved residue as *({conservedResidue
                    ? "Open"
                    : "Close"})
            </Button>
        </div>
        <div
            id="htmlElementId"
            style="height: {36 +
                24 * sequences.length}px;margin-bottom: 12px;margin-top: 12px"
        />
        <Tabs tabStyle="underline">
            <TabItem
                open={active === "edit"}
                title="Edit"
                on:click={() => (active = "edit")}
            >
                <div style="display: flex; flex-direction: row;">
                    <MenuSurface static>
                        <List>
                            {#each sequences as sequence, idx}
                                <Item
                                    activated={activeSequenceId == sequence.id}
                                    on:SMUI:action={() => {
                                        activeSequenceId = sequence.id;
                                        activeSequenceIdx = idx;
                                        currName = sequence.name;
                                    }}
                                >
                                    <div
                                        class="row sequence-editor-label"
                                        style="align-items: center;"
                                    >
                                        <div
                                            class="text-ellipsis"
                                            style="width: 60px"
                                        >
                                            {sequence.name}
                                        </div>
                                        <!-- <Tooltip placement="bottom">{sequence.name}</Tooltip> -->
                                        <svg
                                            width="1em"
                                            height="1em"
                                            viewBox="0 0 14 14"
                                            fill="none"
                                            xmlns="http://www.w3.org/2000/svg"
                                            on:click={(e) => {
                                                e.stopPropagation();
                                                deleteModalVisible = true;
                                            }}
                                        >
                                            <path
                                                d="M14 0H0v14h14V0z"
                                                fill="#fff"
                                                fill-opacity=".01"
                                            />
                                            <path
                                                d="M2.336 2.334l9.333 9.333M2.336 11.667l9.333-9.333"
                                                stroke="#A2A5C4"
                                                stroke-width="1.3"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                            />
                                        </svg>
                                    </div>
                                </Item>
                            {/each}
                        </List>
                    </MenuSurface>
                    <div style="flex: 1; padding-left: 24px;">
                        <div
                            class="row"
                            style="justify-content: center;align-items: center;margin-bottom: 12px;"
                        >
                            <div style="flex: 0 0 120px;">Chain ID</div>
                            <div style="flex: 1;">
                                <Input bind:value={currName} />
                            </div>
                            <Button
                                color="light"
                                style="padding: 0.625rem 1.25rem !important;flex: 0 0 100px;"
                                shape="round"
                                on:click={() => {
                                    saguaroRef?.updateBoardConfig({
                                        boardConfigData:
                                            saguaroRef?.boardConfigData,
                                        rowConfigData:
                                            saguaroRef?.boardDataSate.rowConfigData.map(
                                                (row) => ({
                                                    ...row,
                                                    rowTitle:
                                                        row.trackId.startsWith(
                                                            activeSequence.id,
                                                        )
                                                            ? currName
                                                            : row.rowTitle,
                                                }),
                                            ),
                                    });
                                    updateSequences(
                                        sequences.map((item, index) =>
                                            index === activeSequenceIdx
                                                ? {
                                                      ...item,
                                                      name: currName,
                                                  }
                                                : item,
                                        ),
                                    );
                                }}
                            >
                                Update
                            </Button>
                        </div>

                        <div
                            class="row"
                            style="justify-content: center;align-items: center;margin-bottom: 12px;"
                        >
                            <div style="flex: 0 0 120px;">
                                Selected Sequence {currSelection.begin !== -1
                                    ? `${currSelection.begin} - ${currSelection.end}`
                                    : ""}
                            </div>
                            <Input
                                style="flex: 1;"
                                value={selectionSequences[activeSequenceIdx]}
                                on:change={(e) => {
                                    selectionSequences = selectionSequences.map(
                                        (val, index) =>
                                            index === activeSequenceIdx
                                                ? e.target.value
                                                : val,
                                    );
                                }}
                            />
                            <Button
                                color="light"
                                style="padding: 0.625rem 1.25rem !important;flex: 0 0 100px;"
                                shape="round"
                                disabled={currSelection.begin === -1}
                                on:click={() => {
                                    const newSequence = sequences.map(
                                        (val, index) =>
                                            index === activeSequenceIdx
                                                ? {
                                                      ...val,
                                                      sequence: `${val.sequence.slice(0, currSelection.begin - 1)}${selectionSequences[activeSequenceIdx]}${val.sequence.slice(currSelection.end)}`,
                                                  }
                                                : val,
                                    );
                                    updateSequences(newSequence);
                                    saguaroRef?.updateBoardConfig({
                                        boardConfigData:
                                            saguaroRef?.boardConfigData,
                                        rowConfigData:
                                            saguaroRef?.boardDataSate.rowConfigData.map(
                                                (row) => ({
                                                    ...row,
                                                    displayConfig:
                                                        row.trackId.startsWith(
                                                            activeSequence.id,
                                                        )
                                                            ? getDisplayConfig(
                                                                  newSequence[
                                                                      activeSequenceIdx
                                                                  ].sequence,
                                                              )
                                                            : row.displayConfig,
                                                }),
                                            ),
                                    });
                                }}
                            >
                                Update
                            </Button>
                        </div>

                        <div
                            class="row"
                            style="justify-content: center;align-items: center;margin-bottom: 12px;"
                        >
                            <div style="flex: 0 0 120px;">
                                Complete Sequence
                            </div>
                            <Input
                                style="flex: 1;"
                                value={currSequence[activeSequenceIdx]}
                                on:change={(e) =>
                                    (currSequence = currSequence.map(
                                        (val, index) =>
                                            index === activeSequenceIdx
                                                ? e.target.value
                                                : val,
                                    ))}
                            />
                            <Button
                                color="light"
                                style="padding: 0.625rem 1.25rem !important;flex: 0 0 100px;"
                                shape="round"
                                on:click={() => {
                                    const newSequence = sequences.map(
                                        (val, index) =>
                                            index === activeSequenceIdx
                                                ? {
                                                      ...val,
                                                      sequence:
                                                          currSequence[
                                                              activeSequenceIdx
                                                          ],
                                                  }
                                                : val,
                                    );
                                    updateSequences(newSequence);
                                    saguaroRef?.updateBoardConfig({
                                        boardConfigData:
                                            saguaroRef?.boardConfigData,
                                        rowConfigData:
                                            saguaroRef?.boardDataSate.rowConfigData.map(
                                                (row) => ({
                                                    ...row,
                                                    displayConfig:
                                                        row.trackId.startsWith(
                                                            activeSequence.id,
                                                        )
                                                            ? getDisplayConfig(
                                                                  newSequence[
                                                                      activeSequenceIdx
                                                                  ].sequence,
                                                              )
                                                            : row.displayConfig,
                                                }),
                                            ),
                                    });
                                }}
                            >
                                Update
                            </Button>
                        </div>
                    </div>
                </div>
            </TabItem>
            <TabItem
                open={active === "residueProps"}
                title="Residue Properties"
                on:click={() => (active = "residueProps")}
            >
                <div style="display: flex; flex-direction: row;">
                    <MenuSurface static>
                        <List>
                            {#each sequences as sequence, idx}
                                <Item
                                    activated={viewResidueSequenceId ==
                                        sequence.id}
                                    on:SMUI:action={() => {
                                        viewResidueSequenceId = sequence.id;
                                    }}
                                >
                                    <div
                                        class="row sequence-editor-label"
                                        style="align-items: center;"
                                    >
                                        <div
                                            class="text-ellipsis"
                                            style="width: 60px"
                                        >
                                            {sequence.name}
                                        </div>
                                        <!-- <Tooltip placement="bottom">{sequence.name}</Tooltip> -->
                                    </div>
                                </Item>
                            {/each}
                        </List>
                    </MenuSurface>
                    <div style="padding-left: 24px;">
                        <Table>
                            <TableHead>
                                <TableHeadCell>
                                    <div style="max-width: 60px;">Pos</div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 100px;">Residue</div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 80px;">Name</div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 80px;">Index</div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 60px;">UID</div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 80px;">pKa</div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 100px;">
                                        Polarity
                                    </div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 100px;">
                                        Bulkiness
                                    </div>
                                </TableHeadCell>
                                <TableHeadCell>
                                    <div style="max-width: 60px;">Hyd</div>
                                </TableHeadCell>
                            </TableHead>
                            <TableBody tableBodyClass="divide-y">
                                {#each residuePropsTableData as resProp}
                                    <TableBodyRow>
                                        <TableBodyCell>
                                            <div style="max-width: 60px;">
                                                {resProp.pos}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 100px;">
                                                {resProp.residue}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 80px;">
                                                {resProp.name}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 80px;">
                                                {resProp.index}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 60px;">
                                                {resProp.uid}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 80px;">
                                                {resProp.pKa}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 100px;">
                                                {resProp.polarity}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 100px;">
                                                {resProp.bulkiness}
                                            </div>
                                        </TableBodyCell>
                                        <TableBodyCell>
                                            <div style="max-width: 60px;">
                                                {resProp.hyd}
                                            </div>
                                        </TableBodyCell>
                                    </TableBodyRow>
                                {/each}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            </TabItem>
            <TabItem
                open={active === "chainProps"}
                title="Chain Props"
                on:click={() => (active = "chainProps")}
            >
                <Table>
                    <TableHead>
                        <TableHeadCell>
                            <div style="width: 120px">Chain ID</div>
                        </TableHeadCell>
                        <TableHeadCell>
                            <div>Length</div>
                        </TableHeadCell>
                        <TableHeadCell>
                            <div>pl</div>
                        </TableHeadCell>
                        <TableHeadCell>
                            <div>kDa</div>
                        </TableHeadCell>
                        <TableHeadCell>
                            <div>Hydrophobicity</div>
                        </TableHeadCell>
                    </TableHead>
                    <TableBody>
                        {#each sequenceProps as props}
                            <TableBodyRow>
                                <TableBodyCell>
                                    <div
                                        class="ellipsis-single-line"
                                        style="max-width: 100%"
                                    >
                                        {props.chainId}
                                    </div>
                                    <Tooltip>{props.chainId}</Tooltip>
                                </TableBodyCell>
                                <TableBodyCell>
                                    <div>{props.length}</div>
                                </TableBodyCell>
                                <TableBodyCell>
                                    <div>{props.pl}</div>
                                </TableBodyCell>
                                <TableBodyCell>
                                    <div>{props.kDa}</div>
                                </TableBodyCell>
                                <TableBodyCell>
                                    <div>{props.hydrophobicity}</div>
                                </TableBodyCell>
                            </TableBodyRow>
                        {/each}
                    </TableBody>
                </Table>
            </TabItem>
        </Tabs>
    </div>
    <Modal bind:open={deleteModalVisible} autoclose size="xs">
        <div class="text-center">
            <h3
                class="mb-5 font-normal text-gray-500 dark:text-gray-400"
                style="font-size: 1.125rem !important;margin-bottom: 5px;"
            >
                Confirm to delete?
            </h3>
            <Button
                style="padding: 0.625rem 1.25rem !important;"
                color="alternative"
                class="me-2">Cancel</Button
            >
            <Button
                style="padding: 0.625rem 1.25rem !important;"
                color="red"
                on:click={() => {
                    let maxLength = -1;
                    const newRowConfigData =
                        saguaroRef?.boardDataSate.rowConfigData.filter(
                            (row, index) => {
                                if (index !== activeSequenceIdx) {
                                    maxLength = Math.max(
                                        maxLength,
                                        row.displayConfig.length,
                                    );
                                    return true;
                                }
                                return false;
                            },
                        );
                    saguaroRef?.updateBoardConfig({
                        boardConfigData: saguaroRef?.boardConfigData,
                        rowConfigData: newRowConfigData,
                    });
                    updateSequences(
                        sequences.filter(
                            (_, index) => index !== activeSequenceIdx,
                        ),
                    );
                }}>OK</Button
            >
        </div>
    </Modal>
    <Modal bind:open={inputSequenceModalVisible} autoclose size="xl">
        <SequenceInput
            {gradio}
            submit={(seq) => {
                setSequence(seq);
                inputSequenceModalVisible = false;
            }}
        />
    </Modal>
</div>

<style>
    .row {
        display: flex;
        flex-flow: row wrap;
    }
    .sequence-editor-label {
        font-size: 12px;
    }
    .text-ellipsis {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: start;
    }
    .ellipsis-single-line {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }
    .sequence-editor-table {
        background: #fff;
        color: #000;
        border-color: #000;
        width: 100%;
        overflow: auto;
    }

    .sequence-editor-table-body {
        overflow: auto;
    }
    button {
        padding: 0.625rem 1.25rem !important;
    }
</style>
