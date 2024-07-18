<svelte:options accessors={true} />

<script lang="ts">
    import { onMount } from "svelte";
    import type { Gradio } from "@gradio/utils";
    import type { LoadingStatus } from "@gradio/statustracker";
    import { Button, Tooltip } from "flowbite-svelte";
    import ElementsTable from "./elements-table.svelte";

    enum ButtonType {
        Bond,
        BondMulti,
        ChiralityUp,
        ChiralityDown,
        ChargeAdd,
        ChargeMinus,
        AtomH,
        AtomC,
        AtomO,
        AtomN,
        AtomF,
        AtomSi,
        AtomP,
        AtomS,
        AtomCl,
        EleChart,
        Ring6,
        Ring5,
        RingBenzene,
        Ring3,
        RingN,
        Clean,
        BoxSelection,
        ToggleSelection,
        Erase,
    }
    const ElementList = [
        [
            [ButtonType.AtomH, [16, 0], "H", "Hydrogen"],
            [ButtonType.AtomC, [11, 0], "C", "Carbon"],
        ],
        [
            [ButtonType.AtomO, [13, 0], "O", "Oxygen"],
            [ButtonType.AtomN, [12, 0], "N", "Nitrogen"],
        ],
        [
            [ButtonType.AtomF, [14, 0], "F", "Fluorine"],
            [ButtonType.AtomSi, [11, 1], "Si", "Silicon"],
        ],
        [
            [ButtonType.AtomP, [12, 1], "P", "Phosphorus"],
            [ButtonType.AtomS, [13, 1], "S", "Sulfur"],
        ],
    ];
    const SCALE_STEP = 0.05;
    export let gradio: Gradio<{
        change: never;
        submit: never;
        input: never;
        clear_status: LoadingStatus;
    }>;
    export let OCL;
    export let width;
    export let height;
    export let smiles;
    export let value;
    let editor;
    let containerRef;
    let domRef;
    let scale = 1;
    let eleChartVisible = false;
    let activeButton;
    let hasSelection = false;
    onMount(() => {
        if (!domRef) return;
        editor = new OCL.StructureEditor(domRef, true, 1);
        const { clientWidth: width, clientHeight: height } = domRef;
        editor.drawPane.setSize_0(width, height);
        if (smiles) {
            const mol = OCL.Molecule.fromSmiles(smiles);
            const newMol = editor.model.cleanupAfterPaste(mol.oclMolecule);
            editor.model.setValue(newMol, false);
        }
        editor.setChangeListenerCallback(() => {
            if (editor.toolBar.currentAction.rectangular !== undefined) {
                hasSelection = getSelection().hasSelection;
            }
            value = editor.model.getSmiles_0();
        });
        editor.toolBar.setAction(2, 0);
        activeButton = ButtonType.ToggleSelection
        // @ts-ignore
        // eslint-disable-next-line no-underscore-dangle
        window.__editor = editor;
    });
    const syncSMILES = () => {
        if (editor) {
            const mol = OCL.Molecule.fromSmiles(smiles);
            const newMol = editor.model.cleanupAfterPaste(mol.oclMolecule);
            editor.model.setValue(newMol, false);
        }
    }
    $:smiles, syncSMILES();
    const onScale = (scaleStep: number) => {
        const { mMol } = editor.model;
        const newScale = scale + scaleStep;
        const { clientWidth: width, clientHeight: height } = domRef;
        const center = { x: width / 2, y: height / 2 };
        const rate = newScale / scale;
        mMol.mCoordinates.forEach(
            (atom: { x_0: number; y_0: number }, index: number) => {
                mMol.mCoordinates[index].x_0 =
                    atom.x_0 + (atom.x_0 - center.x) * (rate - 1);
                mMol.mCoordinates[index].y_0 =
                    atom.y_0 + (atom.y_0 - center.y) * (rate - 1);
            },
        );
        scale = newScale;
        editor.drawPane.draw();
    };
    const onMolButtonClick = (type: ButtonType, onActive: () => void) => {
        if (activeButton === type) {
            return;
        }
        if (activeButton === ButtonType.Erase && type !== ButtonType.Erase) {
            editor.model.changeListeners.removeAtIndex(
                editor.model.changeListeners.size() - 1,
            );
            editor.onMouseClicked = () => {};
        }
        activeButton = type;
        onActive();
    };
    const getSelection = () => {
        if (!editor?.model) {
            return {
                includeAtom: [],
                includeBond: [],
                hasSelection: false,
            };
        }
        const { mMol } = editor.model;
        const includeAtom = []; // !!sourceMol.getAllAtoms();
        for (let atom = 0; atom < mMol.getAllAtoms_0(); atom++) {
            includeAtom[atom] = mMol.isSelectedAtom_0(atom);
        }
        const includeBond = [];
        for (let bond = 0; bond < mMol.getAllBonds_0(); bond++) {
            includeBond[bond] = mMol.isSelectedBond_0(bond);
        }
        return {
            includeAtom,
            includeBond,
            hasSelection: !!(
                includeAtom.filter((value) => value).length ||
                includeBond.filter((value) => value).length
            ),
        };
    };
</script>

<div>
    <div
        class="uni-view-ocl-container"
        bind:this={containerRef}
        style="width: {typeof width === 'string'
            ? width
            : `${width}px`}; height: {typeof height === 'string'
            ? height
            : `${height}px`}; background-color: #F2F5FA"
    >
        <div
            view-only="true"
            bind:this={domRef}
            style="width: 100%; height: 100%; background-color: #F2F5FA"
        />
        <div class="uni-view-ocl-toolbar">
            <div class="v-btn-group">
                <div class="v-btn">
                    <svg
                        on:click={() => onScale(SCALE_STEP)}
                        width="16px"
                        height="16px"
                        viewBox="0 0 16 16"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M7.0026 12.6663C10.1322 12.6663 12.6693 10.1293 12.6693 6.99967C12.6693 3.87007 10.1322 1.33301 7.0026 1.33301C3.873 1.33301 1.33594 3.87007 1.33594 6.99967C1.33594 10.1293 3.873 12.6663 7.0026 12.6663Z"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M7 5V9"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M5.00781 7.0052L9.00261 7"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M11.0703 11.0742L13.8987 13.9027"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                </div>
                <div class="v-btn">
                    <svg
                        on:click={() => onScale(-1 * SCALE_STEP)}
                        width="16px"
                        height="16px"
                        viewBox="0 0 16 16"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M7.0026 12.6663C10.1322 12.6663 12.6693 10.1293 12.6693 6.99967C12.6693 3.87007 10.1322 1.33301 7.0026 1.33301C3.873 1.33301 1.33594 3.87007 1.33594 6.99967C1.33594 10.1293 3.873 12.6663 7.0026 12.6663Z"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M5 7H9"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M11.0703 11.0742L13.8987 13.9027"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                </div>
            </div>
        </div>
        <div class="uni-view-ocl-editor">
            <div class="uni-view-ocl-editor-row row-mb">
                <!-- BoxSelection -->
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.BoxSelection}
                    on:click={() => {
                        onMolButtonClick(ButtonType.BoxSelection, () => {
                            editor.toolBar.setAction(2, 0);
                            editor.toolBar.currentAction.rectangular = true;
                        });
                    }}
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                        d="M10.3984 10.3999L15.1984 11.3599L13.7584 12.3199L15.1984 13.7599L13.7584 15.1999L12.3184 13.7599L11.3584 15.1999L10.3984 10.3999Z"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M14 7.5V2H2V13H8"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-dasharray="2 2"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Box selection</span>
                </Tooltip>
                <!-- Toggle Selection -->
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.ToggleSelection}
                    on:click={() => {
                        onMolButtonClick(ButtonType.ToggleSelection, () => {
                            editor.toolBar.setAction(2, 0);
                            editor.toolBar.currentAction.rectangular = false;
                        });
                    }}
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                        d="M10.3984 10.3999L15.1984 11.3599L13.7584 12.3199L15.1984 13.7599L13.7584 15.1999L12.3184 13.7599L11.3584 15.1999L10.3984 10.3999Z"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M14.1688 8.44585C14.9412 7.23045 15.2079 5.87084 14.7952 4.61109C13.907 1.90009 10.2088 0.678104 6.53492 1.88171C2.86106 3.08532 0.60281 6.25874 1.49097 8.96974C1.95795 10.3951 3.20175 11.4089 4.8104 11.8749C5.71712 12.1375 6.73976 12.2262 7.80453 12.1164"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <ellipse
                        cx="3.31885"
                        cy="11.5201"
                        rx="1.86549"
                        ry="1.13858"
                        transform="rotate(-36.0739 3.31885 11.5201)"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M4 13V13.4597C4 13.9276 3.7873 14.3702 3.42191 14.6625V14.6625C3.1488 14.881 2.80945 15 2.45969 15H2"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Toggle selection</span>
                </Tooltip>
            </div>
            <div class="uni-view-ocl-editor-row row-mb">
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.Bond}
                    on:click={() => {
                        onMolButtonClick(ButtonType.Bond, () =>
                            editor.toolBar.setAction(5, 0),
                        );
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M13.387 14.248 1.781 2.641a.649.649 0 0 1 .82-1c.036.024.069.05.099.081L14.307 13.33a.653.653 0 0 1 .08.82.647.647 0 0 1-.789.24.64.64 0 0 1-.21-.14Zm.92 0a.658.658 0 0 1-.46.19.65.65 0 1 1 .46-.19ZM2.7 2.641a.649.649 0 1 1-.918-.917.649.649 0 0 1 .918.917Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Single</span>
                </Tooltip>
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.BondMulti}
                    on:click={() => {
                        onMolButtonClick(ButtonType.BondMulti, () =>
                            editor.toolBar.setAction(5, 1),
                        );
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="m14.796 10.624-4.727-5.09.476-.443.477.442-4.728 5.091a.646.646 0 0 1-.702.167.65.65 0 0 1-.234-.15l-5.09-5.09.919-.92 5.09 5.091-.459.46-.476-.443 4.727-5.09a.661.661 0 0 1 .373-.2.648.648 0 0 1 .58.2l4.727 5.09-.953.885Zm1.127-.442a.642.642 0 0 1-.19.46.647.647 0 0 1-.92 0 .659.659 0 0 1-.19-.46.658.658 0 0 1 .19-.46.654.654 0 0 1 .708-.14.65.65 0 0 1 .402.6ZM1.377 5.09a.648.648 0 0 1-.899.6.648.648 0 0 1-.291-.961.648.648 0 0 1 1.14.112.649.649 0 0 1 .05.249Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Chain</span>
                </Tooltip>
            </div>
            <div class="uni-view-ocl-editor-row row-mb">
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.ChiralityUp}
                    on:click={() => {
                        onMolButtonClick(ButtonType.ChiralityUp, () =>
                            editor.toolBar.setAction(6, 0),
                        );
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path fill="currentColor" d="m1.285 1.286 13.259 9.887-3.372 3.371L1.285 1.286Z" />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Single Up</span>
                </Tooltip>
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.ChiralityDown}
                    on:click={() => {
                        onMolButtonClick(ButtonType.ChiralityDown, () =>
                            editor.toolBar.setAction(6, 1),
                        );
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        fillRule="evenodd"
                        d="m1.286 1.285 2.967 2.213-.754.754-2.213-2.967Zm2.782 3.731.95-.948 1.734 1.294-1.39 1.39-1.294-1.736Zm3.729 5L9.09 11.75l2.662-2.661-1.735-1.294-2.22 2.22Zm-.57-.764 2.025-2.026-1.735-1.294-1.585 1.584 1.295 1.736Zm3.946 5.292L9.66 12.515l2.856-2.855 2.029 1.512-3.372 3.372Z"
                        clipRule="evenodd"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Single Down</span>
                </Tooltip>
            </div>
            <div
                class="uni-view-ocl-editor-row row-mb"
                style="justify-content: start;"
            >
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.Erase}
                    on:click={() => {
                        onMolButtonClick(ButtonType.Erase, () => {
                            editor.toolBar.setAction(2, 0);
                            editor.toolBar.currentAction.rectangular = true;
                            editor.setChangeListenerCallback(() => {
                                const { model } = editor;
                                const { includeAtom } = getSelection();
                                if (!includeAtom.some((item) => item)) return;
                                model.pushUndo();
                                const mol = model.getMolecule_0();
                                mol.deleteAtoms_0(
                                    includeAtom
                                        .map((selected, index) =>
                                            selected ? index : -1,
                                        )
                                        .filter((value) => value > -1),
                                );
                                editor.drawPane.draw();
                                hasSelection = getSelection().hasSelection;
                            });
                            editor.onMouseClicked = () => {
                                const { model } = editor;
                                const curr = model.getSelectedAtom();
                                if (curr < 0) return;
                                model.pushUndo();
                                const mol = model.getMolecule_0();
                                mol.deleteAtoms_0([curr]);
                                editor.drawPane.draw();
                                hasSelection = getSelection().hasSelection;
                            };
                        });
                    }}
                    width="1em"
                    height="1em"
                    viewBox="0 0 20 20"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M1.66669 17.5H18.3334"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M12.9167 1.66669L2.91669 11.6667L5.41669 14.1667H8.75002L17.0834 5.83335L12.9167 1.66669Z"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Erase</span>
                </Tooltip>
            </div>
            <div class="h-split" />

            <div class="uni-view-ocl-editor-row row-mb">
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.ChargeAdd}
                    on:click={() => {
                        onMolButtonClick(ButtonType.ChargeAdd, () =>
                            editor.toolBar.setAction(10, 0),
                        );
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M3.68 11.405c.384.486.835.895 1.355 1.228a.496.496 0 0 1 .222.51.498.498 0 0 1-.675.376.501.501 0 0 1-.087-.044 6.486 6.486 0 0 1-1.599-1.45.493.493 0 0 1-.083-.464.501.501 0 0 1 .868-.155Zm3.034 1.944a5.502 5.502 0 0 0 1.832.124.502.502 0 0 1 .49.734.502.502 0 0 1-.392.261 6.575 6.575 0 0 1-2.163-.146.505.505 0 0 1-.352-.313.495.495 0 0 1 .064-.467.498.498 0 0 1 .521-.193Zm3.59-.354a5.471 5.471 0 0 0 1.509-1.031.496.496 0 0 1 .454-.128.5.5 0 0 1 .24.848 6.463 6.463 0 0 1-1.783 1.22.498.498 0 0 1-.663-.245.505.505 0 0 1 .027-.47.49.49 0 0 1 .217-.194Zm2.598-2.498c.28-.549.462-1.129.546-1.74a.503.503 0 0 1 .466-.43.498.498 0 0 1 .525.567 6.42 6.42 0 0 1-.647 2.058.503.503 0 0 1-.581.254.495.495 0 0 1-.34-.327.497.497 0 0 1 .03-.382Zm.493-3.573a5.427 5.427 0 0 0-.65-1.708.494.494 0 0 1-.02-.47.505.505 0 0 1 .381-.278.499.499 0 0 1 .5.241c.371.63.628 1.304.77 2.02a.492.492 0 0 1-.075.376.503.503 0 0 1-.607.184.501.501 0 0 1-.3-.365ZM11.57 3.817a5.46 5.46 0 0 0-1.567-.94.5.5 0 0 1 .365-.932 6.452 6.452 0 0 1 1.851 1.111.5.5 0 0 1-.65.76ZM8.218 2.504a5.479 5.479 0 0 0-1.82.233.498.498 0 0 1-.644-.527.499.499 0 0 1 .353-.43 6.473 6.473 0 0 1 2.15-.275.498.498 0 0 1 .385.793.499.499 0 0 1-.424.206ZM4.765 3.552c-.5.363-.926.799-1.28 1.305a.5.5 0 1 1-.82-.572 6.486 6.486 0 0 1 1.511-1.542.498.498 0 0 1 .794.384.5.5 0 0 1-.205.425Zm-2.06 2.954A5.486 5.486 0 0 0 2.5 8c0 .622.101 1.224.303 1.805a.498.498 0 0 1-.404.66.501.501 0 0 1-.54-.332A6.457 6.457 0 0 1 1.5 8c0-.602.08-1.19.243-1.765a.498.498 0 0 1 .79-.257.498.498 0 0 1 .172.528Zm4.645 4.16V5.333a.648.648 0 0 1 .898-.6.649.649 0 0 1 .402.6v5.333a.647.647 0 0 1-.65.65.643.643 0 0 1-.46-.19.644.644 0 0 1-.19-.46Zm1.3 0a.647.647 0 0 1-.65.65.643.643 0 0 1-.46-.19.644.644 0 0 1-.178-.586.646.646 0 0 1 .51-.511.65.65 0 0 1 .778.637Zm0-5.333a.648.648 0 0 1-.9.6.649.649 0 1 1 .9-.6Z"
                    />
                    <path
                        fill="currentColor"
                        d="M10.666 8.65H5.333a.649.649 0 1 1 0-1.3h5.333a.65.65 0 1 1 0 1.3Zm.65-.65a.65.65 0 1 1-1.3 0 .65.65 0 0 1 1.3 0ZM5.983 8a.649.649 0 1 1-1.298 0 .649.649 0 0 1 1.298 0Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Increase Charge</span>
                </Tooltip>
                <svg
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.ChargeMinus}
                    on:click={() => {
                        onMolButtonClick(ButtonType.ChargeMinus, () =>
                            editor.toolBar.setAction(10, 1),
                        );
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M3.68 11.405c.384.486.835.895 1.355 1.228a.496.496 0 0 1 .222.51.498.498 0 0 1-.675.376.501.501 0 0 1-.087-.044 6.486 6.486 0 0 1-1.599-1.45.493.493 0 0 1-.083-.464.501.501 0 0 1 .868-.155Zm3.034 1.944a5.502 5.502 0 0 0 1.832.124.502.502 0 0 1 .49.734.502.502 0 0 1-.392.261 6.575 6.575 0 0 1-2.163-.146.505.505 0 0 1-.352-.313.495.495 0 0 1 .064-.467.498.498 0 0 1 .521-.193Zm3.59-.354a5.471 5.471 0 0 0 1.509-1.031.496.496 0 0 1 .454-.128.5.5 0 0 1 .24.848 6.463 6.463 0 0 1-1.783 1.22.498.498 0 0 1-.663-.245.505.505 0 0 1 .027-.47.49.49 0 0 1 .217-.194Zm2.598-2.498c.28-.549.462-1.129.546-1.74a.503.503 0 0 1 .466-.43.498.498 0 0 1 .525.567 6.42 6.42 0 0 1-.647 2.058.503.503 0 0 1-.581.254.495.495 0 0 1-.34-.327.497.497 0 0 1 .03-.382Zm.493-3.573a5.427 5.427 0 0 0-.65-1.708.494.494 0 0 1-.02-.47.505.505 0 0 1 .381-.278.499.499 0 0 1 .5.241c.371.63.628 1.304.77 2.02a.492.492 0 0 1-.075.376.503.503 0 0 1-.607.184.501.501 0 0 1-.3-.365ZM11.57 3.817a5.46 5.46 0 0 0-1.567-.94.5.5 0 0 1 .365-.932 6.452 6.452 0 0 1 1.851 1.111.5.5 0 0 1-.65.76ZM8.218 2.504a5.479 5.479 0 0 0-1.82.233.498.498 0 0 1-.644-.527.499.499 0 0 1 .353-.43 6.473 6.473 0 0 1 2.15-.275.498.498 0 0 1 .385.793.499.499 0 0 1-.424.206ZM4.765 3.552c-.5.363-.926.799-1.28 1.305a.5.5 0 1 1-.82-.572 6.486 6.486 0 0 1 1.511-1.542.498.498 0 0 1 .794.384.5.5 0 0 1-.205.425Zm-2.06 2.954A5.486 5.486 0 0 0 2.5 8c0 .622.101 1.224.303 1.805a.498.498 0 0 1-.404.66.501.501 0 0 1-.54-.332A6.457 6.457 0 0 1 1.5 8c0-.602.08-1.19.243-1.765a.498.498 0 0 1 .79-.257.498.498 0 0 1 .172.528Zm7.961 2.144H5.333a.649.649 0 1 1 0-1.3h5.333a.65.65 0 1 1 0 1.3Zm.65-.65a.65.65 0 1 1-1.3 0 .65.65 0 0 1 1.3 0ZM5.983 8a.649.649 0 1 1-1.298 0 .649.649 0 0 1 1.298 0Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Decrease Charge</span>
                </Tooltip>
            </div>
            <div class="h-split" />
            {#each ElementList as row}
                <div class="uni-view-ocl-editor-row row-mb">
                    {#each row as button}
                        <div
                            on:click={() => {
                                onMolButtonClick(button[0], () =>
                                    editor.toolBar.setAction(
                                        button[1][0],
                                        button[1][1],
                                    ),
                                );
                            }}
                            class="uni-view-ocl-icon"
                            style="font-size: 12px"
                            active={activeButton === button[0]}
                        >
                            {button[2]}
                        </div>
                        <Tooltip>
                            <span class="uni-view-ocl-tooltip">{button[3]}</span>
                        </Tooltip>
                    {/each}
                </div>
            {/each}
            <div class="uni-view-ocl-editor-row row-mb">
                <div
                    on:click={() => {
                        onMolButtonClick(ButtonType.AtomCl, () =>
                            editor.toolBar.setAction(14, 1),
                        );
                    }}
                    class="uni-view-ocl-icon"
                    style="font-size: 12px"
                    active={activeButton === ButtonType.AtomCl}
                >
                    Cl
                </div>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Chlorine</span>
                </Tooltip>
                <svg
                    class="uni-view-ocl-icon"
                    on:click={() => {
                        eleChartVisible = true;
                        activeButton = undefined;
                        editor.toolBar.setAction(2, 0);
                    }}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M14.35 13V3h1.3v10h-1.3Zm.65.65a.65.65 0 1 1 0-1.301.65.65 0 0 1 0 1.301Zm0-10a.649.649 0 1 1 0-1.298.649.649 0 0 1 0 1.298Zm-3 9.5H4v-1.3h8v1.3Zm.65-.65a.65.65 0 1 1-1.301 0 .65.65 0 0 1 1.3 0Zm-8 0a.648.648 0 0 1-.9.6.647.647 0 0 1-.388-.727.65.65 0 0 1 1.288.127ZM12 10.65H4v-1.3h8v1.3Zm.65-.65a.65.65 0 1 1-1.302 0 .65.65 0 0 1 1.302 0Zm-8 0a.648.648 0 0 1-.9.6.647.647 0 0 1-.388-.727.648.648 0 0 1 .999-.413.648.648 0 0 1 .289.54ZM12 8.15H9v-1.3h3v1.3Zm.65-.65a.65.65 0 1 1-1.301 0 .65.65 0 0 1 1.3 0Zm-3 0a.648.648 0 0 1-.777.637.65.65 0 1 1 .777-.637ZM.35 13V3h1.3v10H.35Zm.65.65a.65.65 0 1 1 0-1.301.65.65 0 0 1 0 1.301Zm0-10a.649.649 0 1 1 0-1.298.649.649 0 0 1 0 1.298Z"
                    />
                </svg>
            </div>
            <div class="h-split" />
            <div class="uni-view-ocl-editor-row row-mb">
                <svg
                    on:click={() => {
                        onMolButtonClick(ButtonType.Ring6, () =>
                            editor.toolBar.setAction(8, 1),
                        );
                    }}
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.Ring6}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M8.639 15.055a1.24 1.24 0 0 1-1.279 0l-5.333-2.963c-.452-.25-.677-.635-.677-1.151V5.059c0-.517.225-.9.677-1.151L7.36.945a1.24 1.24 0 0 1 1.279 0l5.333 2.963c.452.25.678.634.678 1.15v5.883c0 .516-.226.9-.678 1.15L8.64 15.056Zm-.631-1.136 5.333-2.963a.016.016 0 0 0 .009-.015V5.059a.016.016 0 0 0-.009-.015L8.008 2.081a.016.016 0 0 0-.016 0L2.658 5.044a.016.016 0 0 0-.008.015v5.882c0 .006.002.011.008.015l5.334 2.963c.005.002.01.002.016 0Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">CycloHexane</span>
                </Tooltip>
                <svg
                    on:click={() => {
                        onMolButtonClick(ButtonType.Ring5, () =>
                            editor.toolBar.setAction(8, 0),
                        );
                    }}
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.Ring5}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M7.19 1.14A1.28 1.28 0 0 1 8 .862c.301 0 .571.092.81.278l5.876 4.58c.224.175.376.4.455.672.08.272.071.542-.024.81l-2.347 6.574a1.287 1.287 0 0 1-.482.633c-.227.16-.48.24-.758.24H4.47a1.29 1.29 0 0 1-.759-.24 1.287 1.287 0 0 1-.481-.633L.883 7.202a1.286 1.286 0 0 1-.024-.81c.079-.273.23-.497.455-.671L7.19 1.14Zm.8 1.025L2.113 6.746c-.007.005-.008.011-.006.019l2.347 6.574a.015.015 0 0 0 .016.01h7.06a.015.015 0 0 0 .016-.01l2.346-6.574c.003-.008.001-.014-.005-.019L8.01 2.166c-.007-.006-.014-.006-.02 0Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">CycloPentane</span>
                </Tooltip>
            </div>
            <div class="uni-view-ocl-editor-row row-mb">
                <svg
                    on:click={() => {
                        onMolButtonClick(ButtonType.RingBenzene, () =>
                            editor.toolBar.setAction(9, 1),
                        );
                    }}
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.RingBenzene}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M8.82 15.08a1.24 1.24 0 0 1-1.278 0l-5.334-2.963c-.451-.25-.677-.634-.677-1.15V5.083c0-.516.226-.9.678-1.15L7.542.97a1.24 1.24 0 0 1 1.279 0l5.333 2.963c.451.251.677.635.677 1.151v5.882c0 .517-.226.9-.677 1.151L8.821 15.08Zm-.63-1.136 5.333-2.963a.016.016 0 0 0 .008-.015V5.084a.015.015 0 0 0-.008-.014L8.189 2.107a.016.016 0 0 0-.016 0L2.84 5.07a.016.016 0 0 0-.009.014v5.882c0 .007.003.012.009.015l5.333 2.963c.006.003.01.003.016 0Z"
                    />
                    <path
                        fill="currentColor"
                        d="m8.322 4.564-3.5 2a.648.648 0 0 1-.97-.61.649.649 0 0 1 .325-.518l3.5-2a.648.648 0 0 1 .939.358.648.648 0 0 1-.294.77ZM12.65 6v4a.642.642 0 0 1-.19.46.648.648 0 0 1-1.11-.46V6a.65.65 0 0 1 1.3 0ZM4.822 9.436l3.5 2a.65.65 0 0 1-.645 1.129l-3.5-2a.65.65 0 0 1 .645-1.13ZM8.65 4a.649.649 0 1 1-1.298 0A.649.649 0 0 1 8.65 4Zm-3.5 2a.649.649 0 1 1-1.298 0A.649.649 0 0 1 5.15 6Zm7.5 0a.643.643 0 0 1-.19.46.644.644 0 0 1-.587.178.646.646 0 0 1-.51-.511A.65.65 0 1 1 12.65 6Zm0 4a.642.642 0 0 1-.19.46.648.648 0 0 1-1.11-.46.65.65 0 0 1 1.3 0Zm-7.5 0a.648.648 0 0 1-.9.6.647.647 0 0 1-.388-.727.648.648 0 0 1 .999-.413.649.649 0 0 1 .289.54Zm3.5 2a.648.648 0 0 1-.9.6.646.646 0 0 1-.388-.727.646.646 0 0 1 .51-.51.65.65 0 0 1 .778.637Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Benzene</span>
                </Tooltip>
                <svg
                    on:click={() => {
                        onMolButtonClick(ButtonType.RingN, () =>
                            editor.toolBar.setAction(7, 1),
                        );
                    }}
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.RingN}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="m5.051 11.056-2.938-2.29c-.007-.005-.008-.011-.006-.019l2.347-6.574a.015.015 0 0 1 .016-.01h7.06c.008 0 .013.003.016.01l2.346 6.574c.003.008.001.014-.005.019l-2.939 2.29.8 1.026 2.938-2.291c.224-.175.376-.398.455-.67.08-.274.071-.544-.024-.811L12.77 1.736a1.287 1.287 0 0 0-.482-.633c-.227-.16-.48-.24-.758-.24H4.47c-.279 0-.531.08-.759.24-.227.16-.388.371-.481.633L.883 8.31a1.286 1.286 0 0 0-.024.81c.079.273.23.497.454.671l2.939 2.29.8-1.025Zm6.947.513a.642.642 0 0 0-.19-.46.638.638 0 0 0-.333-.178.642.642 0 0 0-.488.097.652.652 0 0 0-.099 1 .652.652 0 0 0 1.11-.46Zm-6.696 0a.647.647 0 0 0-.65-.65.643.643 0 0 0-.46.19.644.644 0 0 0-.178.587.65.65 0 0 0 1.288-.127Z"
                    />
                    <path
                        fill="currentColor"
                        d="M6.42 10.717V15h.701v-3.13h.024L9.287 15h.684v-4.283h-.707v3.09H9.24l-2.119-3.09H6.42Zm-2.622-2.98 1.5-4 1.404.526-1.5 4-1.404-.526Zm1.923-3.04a.748.748 0 0 1-.258-1.221.749.749 0 1 1 .258 1.22Zm-1.5 4a.748.748 0 0 1-.145-1.315.749.749 0 1 1 .146 1.315Zm7.981-.96-1.5-4-1.405.526 1.5 4 1.405-.526Zm-.424.96a.75.75 0 1 0-.557-1.393.75.75 0 0 0 .557 1.392Zm-1.5-4.001a.75.75 0 1 0-.557-1.392.75.75 0 0 0 .557 1.392Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Pyrrole</span>
                </Tooltip>
            </div>
            <div
                class="uni-view-ocl-editor-row row-mb"
                style="justify-content: start;"
            >
                <svg
                    on:click={() => {
                        onMolButtonClick(ButtonType.Ring3, () =>
                            editor.toolBar.setAction(7, 0),
                        );
                    }}
                    class="uni-view-ocl-icon"
                    active={activeButton === ButtonType.Ring3}
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        fill="currentColor"
                        d="M.683 12.673 6.86 2.004c.254-.438.633-.657 1.14-.657.506 0 .885.219 1.139.657l6.177 10.67c.254.438.255.878.001 1.317-.253.44-.633.659-1.14.659H1.823c-.508 0-.888-.22-1.141-.66-.253-.439-.253-.878.001-1.317Zm1.125.652a.016.016 0 0 0 0 .016.016.016 0 0 0 .015.009h12.354a.016.016 0 0 0 .014-.009.016.016 0 0 0 0-.016L8.014 2.655A.016.016 0 0 0 8 2.647a.016.016 0 0 0-.015.008l-6.177 10.67Z"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Cyclopropane</span>
                </Tooltip>
            </div>
            <div class="h-split" />
            <div
                class="uni-view-ocl-editor-row row-mb"
                style="justify-content: start;"
            >
                <svg
                    on:click={() => {
                        editor.toolBar.setAction(2, 0);
                        editor.model.pushUndo();
                        editor.model.cleanMolecule(true, true);
                        editor.model.needsLayout(true);
                    }}
                    class="uni-view-ocl-icon"
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                >
                    <path
                        d="M1.60156 8L2.40156 8"
                        stroke="currentColor"
                        stroke-linecap="round"
                    />
                    <path
                        d="M2.6336 7.73248L4.02506 5.44676C4.08027 5.35606 4.18504 5.2998 4.29874 5.2998L7.06109 5.2998C7.17478 5.2998 7.27955 5.35606 7.33477 5.44676L8.72623 7.73248C8.77876 7.81878 8.77876 7.92369 8.72623 8.00999L7.33477 10.2957C7.27955 10.3864 7.17478 10.4427 7.06109 10.4427L4.29874 10.4427C4.18504 10.4427 4.08027 10.3864 4.02506 10.2957L2.6336 8.00999C2.58106 7.92369 2.58106 7.81878 2.6336 7.73248Z"
                        stroke="currentColor"
                        stroke-width="1.3"
                    />
                    <path
                        d="M8.40081 12.9959L7.00935 10.7102C6.95682 10.6239 6.95682 10.519 7.00935 10.4327L8.40081 8.14696C8.45602 8.05625 8.5608 8 8.67449 8L11.4368 8C11.5505 8 11.6553 8.05625 11.7105 8.14696L12.4062 9.28982"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linecap="round"
                    />
                    <path
                        d="M7.0086 5.29009L8.40006 3.00438C8.45527 2.91368 8.56004 2.85742 8.67374 2.85742L11.4361 2.85742C11.5498 2.85742 11.6546 2.91368 11.7098 3.00438L13.1012 5.29009C13.1538 5.37639 13.1538 5.48131 13.1012 5.56761L11.7098 7.85332C11.6546 7.94402 11.5498 8.00028 11.4361 8.00028L8.67374 8.00028C8.56004 8.00028 8.45527 7.94402 8.40006 7.85332L7.0086 5.56761C6.95606 5.48131 6.95606 5.37639 7.0086 5.29009Z"
                        stroke="currentColor"
                        stroke-width="1.3"
                    />
                    <path
                        d="M12.6328 1.8291L11.6027 3.05034"
                        stroke="currentColor"
                        stroke-linecap="round"
                    />
                    <path
                        d="M10.3281 12L11.9948 13.3333L14.6615 10"
                        stroke="#07B166"
                        stroke-width="1.25"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                </svg>
                <Tooltip>
                    <span class="uni-view-ocl-tooltip">Clean</span>
                </Tooltip>
            </div>
        </div>
        {#if eleChartVisible}
            <div class="uni-view-ocl-ele-chart">
                <div
                    class="row"
                    style="justify-content: space-between;margin-bottom: 20px"
                >
                    <span style="font-size: 12px;font-weight: 400;"
                        >Periodic Table</span
                    >
                    <svg
                        class="uni-view-ocl-icon"
                        on:click={() => (eleChartVisible = false)}
                        width="1em"
                        height="1em"
                        viewBox="0 0 14 14"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M14 0H0v14h14V0z"
                            fill="#fff"
                            fill-opacity=".01"
                        />
                        <path
                            d="M2.336 2.334l9.333 9.333M2.336 11.667l9.333-9.333"
                            stroke="currentColor"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                </div>
                <ElementsTable
                    {gradio}
                    onClick={({ atomNo }) => {
                        editor.toolBar.ACTIONS[16][0].theAtomNo = atomNo;
                        editor.toolBar.setAction(16, 0);
                        eleChartVisible = false;
                    }}
                />
            </div>
        {/if}
    </div>
</div>

<style>
    .row {
        display: flex;
        flex-flow: row wrap;
    }
    .uni-view-ocl-container {
        position: relative;
        flex: 1;
        overflow: hidden;
    }
    .uni-view-ocl-toolbar {
        position: absolute;
        right: 16px;
        top: 50%;
        transform: translateY(-50%);
        width: 32px;
    }
    .v-btn-group {
        display: flex;
        flex-direction: column;
        border-radius: 4px;
        background: #ffffff;
        box-shadow:
            0px 6px 10px 0px rgba(183, 192, 231, 0.1),
            0px 8px 12px 1px rgba(170, 181, 223, 0.05);
    }
    .v-btn {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        background: #ffffff;
        box-shadow:
            0px 6px 10px 0px rgba(183, 192, 231, 0.1),
            0px 8px 12px 1px rgba(170, 181, 223, 0.05);
        padding: 8px;
        cursor: pointer;
        color: #a2a5c4 !important;
    }
    .v-btn:hover {
        color: #555878 !important;
    }
    .uni-view-ocl-ele-chart {
        position: absolute;
        top: 8px;
        left: 88px;
        border-radius: 4px;
        background: #ffffff;
        padding: 12px 16px 20px;
        color: #000;
    }
    .uni-view-ocl-editor {
        position: absolute;
        top: 8px;
        left: 16px;
        border-radius: 4px;
        background: #ffffff;
        box-shadow:
            0px 6px 10px 0px rgba(183, 192, 231, 0.1),
            0px 8px 12px 1px rgba(170, 181, 223, 0.05);
        padding: 8px;
        width: 64px;
    }
    .uni-view-ocl-editor-row {
        display: flex;
        flex-flow: row wrap;
        justify-content: center;
        align-items: center;
    }
    .row-mb {
        margin-bottom: 5px;
    }
    .uni-view-ocl-icon {
        font-size: 16px;
        color: #a2a5c4 !important;
        cursor: pointer;
        padding: 4px;
        width: 24px;
        height: 24px;
        display: inline-block;
        text-align: center;
    }
    .uni-view-ocl-icon:hover {
        color: #555878 !important;
    }
    .uni-view-ocl-icon[active="true"] {
        color: #6063f0 !important;
    }
    .h-split {
        width: 40px;
        height: 1px;
        background-color: #eef3fb;
        margin: 8px auto;
    }
    .uni-view-ocl-tooltip {
        padding: 8px 12px;
        background-color: rgba(43, 46, 83, .8);
        box-shadow: 0 2px 5px rgba(82, 99, 175, .2), 0 5px 16px rgba(82, 99, 175, .18);
        min-width: 30px;
        min-height: 32px;
        padding: 6px 8px;
        color: #fff;
        text-align: left;
        text-decoration: none;
        word-wrap: break-word;
        border-radius: 4px;
        display: block;
    }
</style>
