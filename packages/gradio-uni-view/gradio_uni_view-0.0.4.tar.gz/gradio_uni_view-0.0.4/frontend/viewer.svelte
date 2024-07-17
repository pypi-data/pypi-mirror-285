<svelte:options accessors={true} />

<script lang="ts">
    import Textfield from "@smui/textfield";
    import type { Gradio } from "@gradio/utils";
    import { Block } from "@gradio/atoms";
    import type { LoadingStatus } from "@gradio/statustracker";
    import { tick } from "svelte";
    import {
        Granularity,
        LightPlugin,
        Color,
        RepresentationType,
        AtomReprType,
        MolecularReprType,
    } from "dpmol";
    import HorizontalToolbar from "./horizontal-toolbar.svelte";
    import VerticalToolbar from "./vertical-toolbar.svelte";

    export let gradio: Gradio<{
        change: never;
        submit: never;
        input: never;
        clear_status: LoadingStatus;
    }>;
    export let value = "";
    export let height;
    export let structures: any[] = [];
    export let toolbar_visible: boolean;

    const ToolbarWidth = 625;
    window.process = {
        env: {
            NODE_ENV: "production",
            LANG: "",
        },
    };
    // // 'element-symbol' | 'chain-id' | 'residue-name' | 'hydrophobicity' | 'partial-charge' | 'secondary-structure' | 'cdr' | 'uni-fold' | 'em-confidence'
    // const AtomThemeList = [
    //     { label: "Element", value: "element-symbol" },
    //     { label: "Chain", value: "chain-id" },
    //     { label: "Residue", value: "residue-name" },
    //     { label: "Hydrophobicity", value: "hydrophobicity" },
    //     { label: "pKa", value: "partial-charge" },
    //     { label: "Second Structure", value: "secondary-structure" },
    //     { label: "Antibody Structure", value: "cdr" },
    //     { label: "Fold Confidence", value: "uni-fold" },
    //     { label: "EM Confidence", value: "em-confidence" },
    // ];
    // // 'chain-id' | 'residue-name' | 'hydrophobicity' | 'partial-charge' | 'cdr' | 'uni-fold'
    // const SecondStructureThemeList = [
    //     { label: "Chain", value: "chain-id" },
    //     { label: "Residue", value: "residue-name" },
    //     { label: "Hydrophobicity", value: "hydrophobicity" },
    //     { label: "pKa", value: "partial-charge" },
    //     { label: "Antibody Structure", value: "cdr" },
    //     { label: "Fold Confidence", value: "uni-fold" },
    // ];

    // const SurfaceThemeList = [
    //     { label: "Default", value: "uniform" },
    //     { label: "Hydrophobicity", value: "hydrophobicity" },
    //     { label: "Solvent Accesibility", value: "accessible-surface-area" },
    //     { label: "Element", value: "element-symbol" },
    //     { label: "pKa", value: "partial-charge" },
    // ];
    const PresetCarbonColor = new Map([
        ["ligand-default", "#48e533"],
        ["residue-default", "#dcdde8"],
        ["reference", "#f7aa61"],
        ["green", "#01BE77"],
        ["purple", "#7570b3"],
        ["pink", "#e7298a"],
        ["yellow", "#e6ab02"],
        ["brown", "#a6761d"],
        ["gray", "#666666"],
        ["red", "#E41A1C"],
        ["blue", "#3daf4a"],
    ]);

    let lightPlugin = new LightPlugin();

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

    let el: HTMLTextAreaElement | HTMLInputElement;
    const container = true;

    function handle_change(): void {
        gradio.dispatch("change");
    }

    async function handle_keypress(e: KeyboardEvent): Promise<void> {
        await tick();
        if (e.key === "Enter") {
            e.preventDefault();
            gradio.dispatch("submit");
        }
    }

    $: if (value === null) value = "";

    // When the value changes, dispatch the change event via handle_change()
    // See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive
    $: value, handle_change();

    let info = "";

    const updateInfo = () => {
        const label = document.getElementById(`uni-view-label-${key}`);
        if (!label) return;
        if (!info) {
            label.style.display = "none";
            return;
        }
        label.innerHTML = info;
        label.style.display = "block";
    };

    $: info, updateInfo();

    let selectionHistory = 0;
    const init = () => {
        lightPlugin.managers.representation.showPolarHydrogenOnly = false;
        // 修改光照及hover select颜色
        lightPlugin.createCanvas(
            document.getElementById(`uni-view-canvas-${key}`),
            {
                renderer: {
                    ambientIntensity: 0.4,
                    backgroundColor: Color(0xf2f5fa),
                },
            },
        );
        lightPlugin.managers.selection.event.changed.subscribe(() => {
            const { prev } = lightPlugin.managers.selection.structure;
            selectionHistory = prev.length;
        });
        lightPlugin.managers.highlight.info.subscribe((data) => {
            if (!data.info) {
                info = "";
                return;
            }
            if (data.info.type === "Structure") {
                const {
                    granularity,
                    atomName,
                    atomId,
                    altId,
                    residueName,
                    residueId,
                    chainId,
                    emConfidence,
                    bfactor,
                    insertCode,
                    ref,
                } = data.info;
                const molecularName =
                    lightPlugin.managers.cell.getMolecularName(ref);
                switch (granularity) {
                    case "Atom":
                        info = `${molecularName ? `${molecularName} ` : ""}${atomName} ${atomId}${altId} ${residueName} ${residueId}${insertCode ?? ""} ${chainId}${
                            bfactor ? `<p />b-factor: ${bfactor}` : ""
                        }${emConfidence ? `<p />EM Confidence: ${emConfidence}` : ""}`;
                        break;
                    case "Residue":
                        info = `${molecularName ? `${molecularName} ` : ""}${residueName} ${residueId}${
                            insertCode ?? ""
                        } ${chainId}${bfactor ? `<p />b-factor: ${bfactor}` : ""}`;
                        break;
                    case "Chain":
                        info = `${molecularName ? `${molecularName} ` : ""}Chain ${chainId}`;
                        break;
                    default:
                        info = `${molecularName ? `${molecularName} ` : ""}`;
                        break;
                }
                return;
            }
            if (data.info.type === "Interaction") {
                const { interactionType, infoA, infoB } = data.info;
                info = `${interactionType} ${infoA.chainId}:${infoA.residueName}${infoA.residueId}:${infoA.atomName} - ${infoB.chainId}:${infoB.residueName}${infoB.residueId}:${infoB.atomName}`;
                return;
            }
            info = "";
        });
        // @ts-ignore
        // eslint-disable-next-line no-underscore-dangle
        window.__simple_plugin = lightPlugin;
        setTimeout(() => lightPlugin.refresh(), 50);
        handleStructures();
    };
    let isFixedRight = false;
    $: isFixedRight;
    let rootWidth = 0;
    $: rootWidth;
    const interval = setInterval(() => {
        if (
            document.getElementById(`uni-view-canvas-${key}`) &&
            !lightPlugin.canvas3d
        ) {
            clearInterval(interval);
            const observer = new ResizeObserver((entries) => {
                isFixedRight = entries[0].contentRect.width < ToolbarWidth + 18;
                rootWidth = Math.min(
                    entries[0].contentRect.width - 16,
                    ToolbarWidth,
                );
                resize();
            });
            observer.observe(document.getElementById(`uni-view-canvas-${key}`));
            init();
        }
    }, 1000);
    const resize = () => {
        setTimeout(() => {
            lightPlugin.refresh({ fixCamera: true });
        }, 0);
    };
    $: height, resize();
    const colorHexToNumber = (color = "#F2F5FA") => {
        if (color.startsWith("#")) {
            color = color.substr(1);
        }
        return parseInt(color, 16);
    };
    const handleStructures = () => {
        lightPlugin.clear();
        if (!lightPlugin.canvas3d) return;
        structures.forEach((item) => {
            const {
                format,
                content,
                reprType,
                carbonColor,
                ribbonTheme,
                atomTheme,
            } = item;
            if (!MolecularReprType.has(reprType) || !content) return;
            const theme = {};
            if (carbonColor && (atomTheme === "element-symbol" || !atomTheme)) {
                Object.assign(theme, {
                    Atom: {
                        color: {
                            name: "element-symbol",
                            props: {
                                carbonColor: {
                                    name: "uniform",
                                    params: {
                                        value: Color(
                                            colorHexToNumber(
                                                PresetCarbonColor.get(
                                                    carbonColor,
                                                ) ?? carbonColor,
                                            ),
                                        ),
                                    },
                                },
                            },
                        },
                    },
                });
            }
            if (atomTheme) {
                if (atomTheme !== "element-symbol")
                    Object.assign(theme, {
                        Atom: {
                            color: {
                                name: atomTheme,
                            },
                        },
                    });
            }
            if (ribbonTheme) {
                Object.assign(theme, {
                    Ribbon: {
                        color: {
                            name: ribbonTheme,
                        },
                    },
                });
            }
            lightPlugin.managers.representation.createMolecular({
                format,
                data: content,
                reprType:
                    reprType ??
                    (format === "pdb"
                        ? RepresentationType.Ribbon
                        : RepresentationType.BallAndStick),
                theme,
            });
        });
    };

    $: structures, handleStructures();
</script>

<div
    class="uni-view-container"
    style={height !== undefined ? `height: ${height}px;` : ""}
>
    <div id="uni-view-canvas-{key}" class="uni-view-canvas"></div>
    {#if toolbar_visible}
        <HorizontalToolbar
            {gradio}
            {lightPlugin}
            {isFixedRight}
            {rootWidth}
            {selectionHistory}
        />
    {/if}
    {#if toolbar_visible}
        <VerticalToolbar {gradio} {lightPlugin} />
    {/if}
    {#if !toolbar_visible}
        <div class="uni-view-toolbar">
            <button
                class="uni-view-toolbar-btn"
                on:click={() => lightPlugin.managers.camera.zoomIn()}
            >
                <svg
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M8.02 3.334l-.012 9.333M3.336 8h9.333"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                </svg>
            </button>
            <button
                class="uni-view-toolbar-btn"
                on:click={() => lightPlugin.managers.camera.zoomOut()}
            >
                <svg
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M3.336 8h9.333"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                </svg>
            </button>
            <button
                class="uni-view-toolbar-btn"
                on:click={() => lightPlugin.managers.camera.focus()}
            >
                <svg
                    width="1em"
                    height="1em"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M8.0026 14.6673C11.6845 14.6673 14.6693 11.6825 14.6693 8.00065C14.6693 4.31875 11.6845 1.33398 8.0026 1.33398C4.32071 1.33398 1.33594 4.31875 1.33594 8.00065C1.33594 11.6825 4.32071 14.6673 8.0026 14.6673Z"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M8 12.334V14.6673"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M12 8H14.6667"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M1.33594 8H3.66927"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <path
                        d="M8 3.66732V1.33398"
                        stroke="#A2A5C4"
                        stroke-width="1.3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                    />
                    <circle cx="8" cy="8" r="1" stroke="#A2A5C4" />
                </svg>
            </button>
        </div>
    {/if}
    <div
        id="uni-view-label-{key}"
        class="uni-view-label"
        style="display: none;"
    />
    <!-- <div style="display: flex;flex-direction: column;">
        {#each [
            ['ligand-default', '#48e533'],
            ['residue-default', '#dcdde8'],
            ['reference', '#f7aa61'],
            ['green', '#01BE77'],
            ['purple', '#7570b3'],
            ['pink', '#e7298a'],
            ['yellow', '#e6ab02'],
            ['brown', '#a6761d'],
            ['gray', '#666666'],
            ['red', '#E41A1C'],
            ['blue', '#377eb8'],] as item}
            <div>
            <div style="width: 90px; text-align: end;display: inline-block;line-height: 20px;height: 20px;">{item[0]}</div>
            <div style="
    width: 8px;
    height: 8px;
    border-radius: 2px;
    margin-left: 8px;
    display: inline-block;background: {item[1]};line-height: 20px;margin-top: 6px;"></div></div>
        {/each}
    </div> -->
</div>

<style>
    .uni-view-container {
        width: 100%;
        height: 100%;
        position: relative;
        min-height: 240px;
    }
    .uni-view-canvas {
        width: 100%;
        height: 100%;
        min-height: 240px;
    }
    .uni-view-toolbar {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        flex-direction: column;
        color: #000000;

        background: #ffffff;
        box-shadow:
            0 6px 10px rgba(183, 192, 231, 0.1),
            0 8px 12px 1px rgba(170, 181, 223, 0.05);
        border-radius: 4px;
        padding: 4px;
        margin-bottom: 8px;
    }
    .uni-view-toolbar-btn {
        cursor: pointer;
        font-size: 16px;
        height: 16px;
        width: 16px;
        margin-bottom: 4px;
    }
    .uni-view-toolbar-btn:hover {
        cursor: pointer;
        color: #555878;
    }
    .uni-view-label {
        background: #555878;
        opacity: 0.8;
        border-radius: 4px;
        color: #ffffff;
        position: absolute;
        left: 0px;
        bottom: 0px;
        z-index: 999;
        padding: 4px 8px;
        bottom: 0;
    }
</style>
