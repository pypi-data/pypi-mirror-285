<svelte:options accessors={true} />

<script lang="ts">
    import Textfield from "@smui/textfield";
    import type { Gradio } from "@gradio/utils";
    import type { LoadingStatus } from "@gradio/statustracker";
    import {
        Granularity,
        RepresentationType,
        HierarchyType,
        queryCellItemsByHierarchyType,
        CellItem,
        sliceCellItemsByGranularity,
        InteractionOptions,
        INTERACTION_TYPE,
    } from "dpmol";
    import { KRadio } from "@ikun-ui/radio";
    import { KRadioGroup } from "@ikun-ui/radio-group";
    import { KDropdown, KDropdownItem } from "@ikun-ui/dropdown";
    import { KCheckbox } from "@ikun-ui/checkbox";
    import { KCheckboxGroup } from "@ikun-ui/checkbox-group";
    import { Button, Tooltip } from "flowbite-svelte";
    import "./index.less";
    import "./index.css";
    import "./flowbite-svelte.css";

    enum ExpandFilter {
        All = 0,
        Residues,
        Water,
        SolventWithoutWater,
        Solvent,
    }
    export let gradio: Gradio<{
        change: never;
        submit: never;
        input: never;
        clear_status: LoadingStatus;
    }>;
    export let lightPlugin;
    export let isFixedRight;
    export let rootWidth;
    export let selectionHistory;

    const NonCovalentBondsOption = [
        {
            label: "Hydrogen Bonds",
            value: InteractionOptions.HydrogenBonds,
            color: "#FF9C33",
        },
        {
            label: "Weak H-Bonds",
            value: InteractionOptions.WeakHydrogenBonds,
            color: "#FFE89F",
        },
        {
            label: "Halogen Bonds",
            value: InteractionOptions.HalogenBonds,
            color: "#5DE8EA",
        },
        {
            label: "Salt Bridge",
            value: InteractionOptions.SaltBridge,
            color: "#F164F3",
        },
        // { label: 'Metal Bond', value: 'metalBond', color: '#B1B4D3' },
        {
            label: "Aromatic H-Bond",
            value: "arHbond",
            disabled: true,
            color: "#A68EFF",
        },
    ];
    const ElectrostaticOption = [
        {
            label: "Pi-Pi Stacking",
            value: InteractionOptions.PiPiStacking,
            color: "#43B3F9",
        },
        {
            label: "Pi-Cations",
            value: InteractionOptions.PiCations,
            color: "#33C46D",
        },
    ];
    const ContactOrClashesOption = [
        { label: "Good", value: "good", disabled: true },
        { label: "Bad", value: "bad", disabled: true },
        { label: "Ugly", value: "ugly", disabled: true },
    ];
    const InteractionTypeOption = [
        { label: "All", value: INTERACTION_TYPE.All },
        { label: "Ligand-Receptor", value: INTERACTION_TYPE.LigandReceptor },
        { label: "Intra-Ligand", value: INTERACTION_TYPE.IntraLigand },
        { label: "Intra-Receptor", value: INTERACTION_TYPE.IntraReceptor },
    ];
    let style = "";
    const updateStyle = () => {
        style = `width: ${expanded ? rootWidth : 46}px; overflowX: ${isFixedRight ? "scroll" : "hidden"}`;
    };
    $: isFixedRight, updateStyle();
    $: rootWidth, updateStyle();
    let expanded = true;

    let pickModeVisible = false;
    $: pickModeVisible;

    let currGranularity = Granularity.Residue;
    const pickLevelText = (currGranularity) => {
        if (currGranularity === Granularity.Atom) return "Atom";
        if (currGranularity === Granularity.Residue) return "Residue";
        if (currGranularity === Granularity.Chain) return "Chain";
        if (currGranularity === Granularity.Molecular) return "Molecule";
        return "Residue";
    };
    const quickSelect = (type: HierarchyType) => {
        const func = () => {
            lightPlugin.managers.selection.structure.clear();
            const queryData = queryCellItemsByHierarchyType(lightPlugin);
            Object.keys(queryData).forEach((ref) => {
                const item = queryData[ref];
                const data =
                    type === HierarchyType.Solvent
                        ? [...item[type], ...item[HierarchyType.Water]]
                        : item[type];
                if (data.length) {
                    lightPlugin.managers.selection.structure.add(
                        {
                            item: {
                                ref,
                                elementIds:
                                    (data
                                        .map((item) => item.elementIds)
                                        .flat() as number[]) ?? [],
                            },
                        },
                        false,
                    );
                }
            });
        };
        func();
    };

    const changeRepr = (type: RepresentationType, hideOther: boolean) => {
        if (!selectionHistory) return;
        const items =
            lightPlugin.managers.selection.structure.getSelectionCellItems();
        lightPlugin.managers.representation.setMolecularRepr(
            items,
            type,
            hideOther,
        );
    };
    const addMeasurement = async (
        items: CellItem[],
        type: RepresentationType,
    ) => {
        await lightPlugin.managers.representation.createMeasurement({
            items,
            type,
        });
    };
    const addLabel = async (
        items: Array<CellItem & { props: any }>,
        granularity: Granularity,
    ) => {
        const getCustomText = (data: any, granularity: Granularity) => {
            if (granularity === Granularity.Molecular) return undefined;
            if (granularity === Granularity.Chain) return `${data.chainId}`;
            if (granularity === Granularity.Residue)
                return `${data.residueName} ${data.residueId}`;
            if (granularity === Granularity.Atom)
                return `${data.atomName} ${data.atomId}`;
            return "unknown";
        };
        const data = items.map(({ props, ...item }) => ({
            ...item,
            customText: getCustomText(
                { ...props, cRef: item.ref },
                granularity,
            ),
        }));
        const cRefs = await Promise.all(
            data.map(({ customText, ...item }) =>
                lightPlugin.managers.representation.createMeasurement({
                    items: [item],
                    type: RepresentationType.Label,
                    props: {
                        // ...preferencesForTheme.label,
                        customText,
                    },
                }),
            ),
        );
        return cRefs;
    };
    let surroundingDropdownRef: any = null;
    let surroundingVisible = false;
    $: surroundingVisible;
    let surroundingRadius = 3;
    $: surroundingRadius;
    let expandFilter = ExpandFilter.All;
    $: expandFilter;
    let asWholeResidueState = 1;
    $: asWholeResidueState;
    let excludeSelectedAtoms = false;
    $: excludeSelectedAtoms;
    let measureVisible = false;
    let labelVisible = false;
    let interactionState = false;
    let interactionVisible = false;
    let nonCovalentBondsSetting = [
        InteractionOptions.HydrogenBonds,
        InteractionOptions.HalogenBonds,
        InteractionOptions.SaltBridge,
    ];
    let electrostaticSetting = [
        InteractionOptions.PiPiStacking,
        InteractionOptions.PiCations,
    ];
    let interactionType = INTERACTION_TYPE.LigandReceptor;
    let interactionDropdownRef;
    let hydrogenDropdownRef;
    let isShowPolar = 1;
    let isShowNoPolar = 1;
</script>

<div class="uni-view-horizontal-toolbar-container">
    {#if lightPlugin.canvas3d}
        <div {style} class="uni-view-horizontal-toolbar-inner row">
            <!-- Quick Select -->
            <div style="margin: 4px 8px;">
                <div class="uni-view-horizontal-toolbar-title row">
                    Quick Select
                </div>
                <div class="row">
                    <div
                        class="uni-view-horizontal-toolbar-item"
                        style={expanded ? "" : `position: relative;top: -8px;`}
                    >
                        <KDropdown
                            on:change={(e) => {
                                pickModeVisible = e.detail;
                            }}
                            on:command={(e) => {
                                currGranularity = e.detail;
                                lightPlugin.managers.selection.structure.setGranularity(
                                    e.detail,
                                );
                            }}
                            trigger="click"
                        >
                            <div
                                class="row"
                                style={"flex-shrink: 0; align-items: center; justify-content: center;"}
                            >
                                <!-- <Wrapper> -->
                                <div>
                                    {#if currGranularity === Granularity.Atom}
                                        <svg
                                            width="1em"
                                            height="1em"
                                            viewBox="0 0 20 20"
                                            fill="none"
                                            xmlns="http://www.w3.org/2000/svg"
                                            class="normal-icon"
                                        >
                                            <path
                                                d="M20 0H0v20h20V0z"
                                                fill="#fff"
                                                fill-opacity=".01"
                                            />
                                            <circle
                                                cx="10"
                                                cy="10"
                                                r="1.25"
                                                fill="#A2A5C4"
                                            />
                                            <path
                                                d="M16.908 3.062c1.569 1.569-.26 5.94-4.083 9.763-3.823 3.824-8.194 5.652-9.763 4.083-1.569-1.569.26-5.94 4.083-9.763 3.823-3.824 8.194-5.652 9.763-4.083z"
                                                stroke="#A2A5C4"
                                                stroke-width="1.3"
                                                stroke-linecap="square"
                                                stroke-linejoin="round"
                                            />
                                            <path
                                                d="M3.117 3.062c-1.569 1.569.259 5.94 4.082 9.763 3.824 3.824 8.195 5.652 9.764 4.083 1.568-1.569-.26-5.94-4.083-9.763C9.056 3.32 4.685 1.493 3.117 3.062z"
                                                stroke="#A2A5C4"
                                                stroke-width="1.3"
                                                stroke-linecap="square"
                                                stroke-linejoin="round"
                                            />
                                        </svg>
                                    {/if}
                                    {#if currGranularity === Granularity.Residue}
                                        <svg
                                            class="normal-icon"
                                            width="1em"
                                            height="1em"
                                            viewBox="0 0 20 20"
                                            fill="none"
                                            xmlns="http://www.w3.org/2000/svg"
                                        >
                                            <path
                                                d="M17.071 5.596l-6.666-3.704a.833.833 0 0 0-.81 0L2.93 5.596a.833.833 0 0 0-.429.728v7.353c0 .302.164.581.429.728l6.666 3.704c.252.14.558.14.81 0l6.666-3.704M5.5 12.5L10 15"
                                                stroke="#A2A5C4"
                                                stroke-width="1.3"
                                                stroke-linecap="round"
                                            />
                                            <path
                                                stroke="#A2A5C4"
                                                stroke-linecap="round"
                                                stroke-dasharray="1 2"
                                                d="M17.5 7.5v5"
                                            />
                                        </svg>
                                    {/if}
                                    {#if currGranularity === Granularity.Chain}
                                        <svg
                                            class="normal-icon"
                                            width="1em"
                                            height="1em"
                                            viewBox="0 0 20 20"
                                            fill="none"
                                            xmlns="http://www.w3.org/2000/svg"
                                        >
                                            <path
                                                d="M12.9141 8.75032L14.5807 7.50033L18.3307 10.0003V14.167L14.1641 16.667L9.99739 14.167V5.41699L5.41406 2.91699L1.66406 5.41699V10.0003L5.41406 12.5003L7.08073 11.2503"
                                                stroke="#A2A5C4"
                                                stroke-width="1.3"
                                                stroke-linecap="square"
                                                stroke-linejoin="round"
                                            />
                                        </svg>
                                    {/if}
                                    {#if currGranularity === Granularity.Molecular}
                                        <svg
                                            class="normal-icon"
                                            width="1em"
                                            height="1em"
                                            viewBox="0 0 20 20"
                                            fill="none"
                                            xmlns="http://www.w3.org/2000/svg"
                                        >
                                            <path
                                                d="M20 0H0V20H20V0Z"
                                                fill="white"
                                                fill-opacity="0.01"
                                            />
                                            <path
                                                d="M17.9167 14.9993C17.9167 15.5583 17.6965 16.0659 17.3382 16.4401C16.959 16.8361 16.425 17.0827 15.8333 17.0827C14.6827 17.0827 13.75 16.1499 13.75 14.9993C13.75 14.1618 14.2442 13.4397 14.957 13.1088C15.2233 12.9851 15.5203 12.916 15.8333 12.916C16.9839 12.916 17.9167 13.8488 17.9167 14.9993Z"
                                                stroke="#A2A5C4"
                                                stroke-width="1.25"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                            />
                                            <path
                                                d="M6.2526 14.9993C6.2526 15.5583 6.03244 16.0659 5.67415 16.4401C5.2949 16.8361 4.7609 17.0827 4.16927 17.0827C3.01868 17.0827 2.08594 16.1499 2.08594 14.9993C2.08594 14.1618 2.58016 13.4397 3.29288 13.1088C3.55929 12.9851 3.85622 12.916 4.16927 12.916C5.31985 12.916 6.2526 13.8488 6.2526 14.9993Z"
                                                stroke="#A2A5C4"
                                                stroke-width="1.25"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                            />
                                            <path
                                                d="M12.0807 3.74935C12.0807 4.30835 11.8606 4.81589 11.5023 5.19006C11.123 5.5861 10.589 5.83268 9.9974 5.83268C8.84681 5.83268 7.91406 4.89993 7.91406 3.74935C7.91406 2.91181 8.40827 2.18971 9.12102 1.85877C9.3874 1.73507 9.68435 1.66602 9.9974 1.66602C11.148 1.66602 12.0807 2.59876 12.0807 3.74935Z"
                                                stroke="#A2A5C4"
                                                stroke-width="1.25"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                            />
                                            <path
                                                d="M9.99996 11V6M9.99996 11L5.625 13.5259L9.99996 11ZM9.99996 11L14.3749 13.5259L9.99996 11Z"
                                                stroke="#A2A5C4"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                                stroke-dasharray="2 2"
                                            />
                                            <path
                                                d="M9 5.5L4 13M11 5.5L16 13"
                                                stroke="#A2A5C4"
                                                stroke-linejoin="round"
                                            />
                                            <path
                                                d="M6 15L14 15"
                                                stroke="#A2A5C4"
                                                stroke-linejoin="round"
                                            />
                                        </svg>
                                    {/if}
                                </div>
                                <Tooltip>
                                    {`Pick ${pickLevelText(currGranularity)}`}
                                </Tooltip>
                                <!-- </Wrapper> -->
                                <svg
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 8 8"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    style={`
                                    transform: ${pickModeVisible ? "rotate(0)" : "rotate(180deg)"};
                                    font-size: 8px;
                                    color: #a2a5ca;
                                `}
                                >
                                    <path
                                        d="M6.95641 5.66979L4.15766 2.07713C4.07755 1.97429 3.9233 1.97429 3.84234 2.07713L1.04359 5.66979C0.939613 5.80376 1.03336 6 1.20125 6L6.79875 6C6.96664 6 7.06039 5.80376 6.95641 5.66979Z"
                                        fill="#888BAB"
                                    />
                                </svg>
                            </div>
                            <div slot="dropdown" class="menu-normal">
                                <KDropdownItem command={Granularity.Atom}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <AtomIcon className={styles['normal-icon']} /> -->
                                        Atom
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem command={Granularity.Residue}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ResidueIcon className={styles['normal-icon']} /> -->
                                        Residue
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem command={Granularity.Chain}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ChainIcon className={styles['normal-icon']} /> -->
                                        Chain
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem command={Granularity.Molecular}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <MolecularIcon className={styles['normal-icon']} /> -->
                                        Molecule
                                    </div>
                                </KDropdownItem>
                            </div>
                        </KDropdown>
                        <div class={"uni-view-horizontal-toolbar-subtitle"}>
                            {pickLevelText(currGranularity)}
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() => quickSelect(HierarchyType.Protein)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            xmlns="http://www.w3.org/2000/svg"
                            width="1em"
                            height="1em"
                            fill="none"
                            viewBox="0 0 20 20"
                        >
                            <path
                                fill="#A2A5C4"
                                d="M10.61 8.936a.6.6 0 0 1 .6-.6h3.543c2.38 0 3.57 1.008 3.57 3.038 0 2.044-1.204 3.066-3.598 3.066h-2.59v3.292a.6.6 0 0 1-.6.6h-.326a.6.6 0 0 1-.6-.6V8.936Zm1.525.702v3.5h2.492c.756 0 1.302-.14 1.652-.42.336-.28.518-.728.518-1.344 0-.616-.182-1.064-.532-1.316-.35-.28-.896-.42-1.638-.42h-2.492Z"
                            />
                            <path
                                stroke="#A2A5C4"
                                stroke-linecap="round"
                                stroke-width="1.3"
                                d="m9.607 7.14-.283-.826s-.118-1.327.699-2.564 2.184-1.61 2.184-1.61l1.892 4.174"
                            />
                            <path
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                                d="M3.738 8.955C4.556 7.718 5.61 7.32 5.61 7.32l2.053 4.927s.362 1.252-.291 2.241c-.653.99-1.86 2.097-2.05 2.207l-2.188-5.714s-.213-.79.604-2.027Z"
                            />
                            <path
                                stroke="#A2A5C4"
                                stroke-linecap="round"
                                stroke-width="1.3"
                                d="M9.472 7.146 8.77 6.99s-1.9-.575-3.512.463c-1.181.76-1.812 2.398-1.912 2.64l3.064.786 1.531.393.766.196"
                            />
                        </svg>
                        <!-- <Tooltip trigger={['hover', 'click']} title="Select Proteins" placement="bottom"> -->
                        <!-- </Tooltip> -->
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Protein
                        </div>
                    </div>

                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() => quickSelect(HierarchyType.Ligand)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            xmlns="http://www.w3.org/2000/svg"
                            width="1em"
                            height="1em"
                            fill="none"
                            viewBox="0 0 20 20"
                        >
                            <path
                                stroke="#A2A5C4"
                                stroke-linecap="round"
                                d="M1.664 8.858h1.273"
                            />
                            <path
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                                d="m3.011 8.697 1.616-2.654a.37.37 0 0 1 .318-.17h3.208a.37.37 0 0 1 .318.17l1.616 2.654c.061.1.061.222 0 .323l-1.616 2.654a.37.37 0 0 1-.318.17H4.945a.37.37 0 0 1-.318-.17L3.011 9.02a.307.307 0 0 1 0-.323Z"
                            />
                            <path
                                stroke="#A2A5C4"
                                stroke-linecap="round"
                                stroke-width="1.3"
                                d="m9.96 9.246-1.615 2.655a.307.307 0 0 0 0 .322l1.616 2.654m.159-6.13L8.502 6.093a.307.307 0 0 1 0-.322l1.616-2.655a.37.37 0 0 1 .318-.17h3.208a.37.37 0 0 1 .318.17l1.616 2.655c.061.1.061.222 0 .322l-.85 1.413"
                            />
                            <path
                                stroke="#A2A5C4"
                                stroke-linecap="round"
                                d="M14.906 1.661 13.71 3.08"
                            />
                            <path
                                fill="#A2A5C4"
                                d="M11.563 9.3a.6.6 0 0 1 .6-.6h.256a.6.6 0 0 1 .6.6v7.773h4.7a.6.6 0 0 1 .6.6v.054a.6.6 0 0 1-.6.6h-5.557a.6.6 0 0 1-.6-.6V9.3Z"
                            />
                        </svg>
                        <!-- <Tooltip trigger={['hover', 'click']} title="Select Proteins" placement="bottom"> -->
                        <!-- </Tooltip> -->
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Ligand
                        </div>
                    </div>

                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() => quickSelect(HierarchyType.Solvent)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            xmlns="http://www.w3.org/2000/svg"
                            width="1em"
                            height="1em"
                            fill="none"
                            viewBox="0 0 20 20"
                        >
                            <path
                                stroke="#A2A5C4"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="1.3"
                                d="M8.636 14.942H2.315a.666.666 0 0 1-.667-.667v0c0-.174.069-.34.19-.465l1.654-1.692a1 1 0 0 1 .714-.3l4.423-.006m-4.848.011 2.474-2.53a1 1 0 0 0 .285-.699V2.665a1 1 0 0 1 1-1h2.192a1 1 0 0 1 1 1v4.503m-.003-2.708H8.633m2.096 2.097H8.633"
                            />
                            <path
                                fill="#A2A5C4"
                                d="M14.2 7.975c1.163 0 2.073.238 2.73.742.554.409.915.993 1.09 1.76.079.343-.203.648-.556.648h-.372c-.282 0-.52-.2-.615-.466-.148-.411-.362-.727-.652-.934-.392-.294-.952-.434-1.708-.434-.658 0-1.162.098-1.512.294-.434.224-.644.588-.644 1.092 0 .448.238.798.742 1.064.224.126.798.336 1.736.616 1.344.42 2.226.742 2.618.98.854.518 1.288 1.232 1.288 2.156 0 .896-.35 1.596-1.05 2.114-.7.504-1.68.756-2.94.756-1.218 0-2.17-.252-2.856-.728-.68-.485-1.104-1.196-1.28-2.136-.063-.341.216-.636.563-.636h.35c.299 0 .546.221.625.51.146.526.391.925.736 1.184.406.308 1.022.462 1.862.462.756 0 1.358-.14 1.806-.392.448-.252.672-.602.672-1.05 0-.56-.322-.994-.952-1.316-.224-.112-.882-.336-1.988-.672-1.232-.392-1.988-.658-2.296-.826-.77-.462-1.148-1.134-1.148-2.002 0-.882.364-1.568 1.106-2.072.7-.476 1.582-.714 2.646-.714Z"
                            />
                        </svg>
                        <!-- <Tooltip trigger={['hover', 'click']} title="Select Proteins" placement="bottom"> -->
                        <!-- </Tooltip> -->
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Solvent
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <KDropdown
                            on:change={(e) => {
                                surroundingVisible = e.detail;
                            }}
                            on:command={(e) => {
                                currGranularity = e.detail;
                                lightPlugin.managers.selection.structure.setGranularity(
                                    e.detail,
                                );
                            }}
                            bind:this={surroundingDropdownRef}
                            trigger="click"
                        >
                            <svg
                                class="uni-view-horizontal-toolbar-icon {!selectionHistory
                                    ? 'disabled'
                                    : ''}"
                                width="1em"
                                height="1em"
                                viewBox="0 0 20 20"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path
                                    d="M18.3346 10.0003C18.3346 5.39795 14.6037 1.66699 10.0013 1.66699C5.39893 1.66699 1.66797 5.39795 1.66797 10.0003C1.66797 14.6027 5.39893 18.3337 10.0013 18.3337"
                                    stroke="#A2A5C4"
                                    stroke-width="1.3"
                                    stroke-linecap="round"
                                />
                                <path
                                    d="M10 12C11.1046 12 12 11.1046 12 10C12 8.89543 11.1046 8 10 8C8.89543 8 8 8.89543 8 10C8 11.1046 8.89543 12 10 12Z"
                                    fill="#A2A5C4"
                                    stroke="#A2A5C4"
                                    stroke-width="1.3"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                                <path
                                    fill-rule="evenodd"
                                    clip-rule="evenodd"
                                    d="M13 13L19 14.2L17.2 15.4L19 17.2L17.2 19L15.4 17.2L14.2 19L13 13Z"
                                    stroke="#A2A5C4"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                />
                            </svg>
                            <div slot="dropdown">
                                <div
                                    class="uni-view-horizontal-toolbar-surrounding-container"
                                >
                                    <div class="row" style="color: #888BAB;">
                                        By Radius
                                        <svg
                                            style="margin-left: 6px"
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
                                                d="M6.997 12.833c1.611 0 3.07-.653 4.125-1.709A5.815 5.815 0 0 0 12.831 7c0-1.61-.653-3.069-1.709-4.124a5.815 5.815 0 0 0-4.125-1.709c-1.61 0-3.069.653-4.124 1.709a5.815 5.815 0 0 0-1.709 4.124c0 1.611.653 3.07 1.709 4.125a5.815 5.815 0 0 0 4.124 1.709z"
                                                stroke="#A2A5C4"
                                                stroke-width="1.3"
                                                stroke-linejoin="round"
                                            />
                                            <path
                                                fill-rule="evenodd"
                                                clip-rule="evenodd"
                                                d="M7.003 3.209a.73.73 0 1 1 0 1.458.73.73 0 0 1 0-1.458z"
                                                fill="#A2A5C4"
                                            />
                                            <path
                                                d="M7.146 9.917V5.834h-.584M6.125 9.916h2.042"
                                                stroke="#A2A5C4"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                            />
                                        </svg>
                                        <Tooltip>
                                            Expand Selection by Radius and
                                            Include Full Residue.
                                        </Tooltip>
                                    </div>
                                    <Textfield
                                        bind:value={surroundingRadius}
                                        label="Number with Step"
                                        type="number"
                                        input$step="1"
                                        suffix="Å"
                                        style="color: #000000"
                                    />
                                    <!-- <Input>
                                    <input type="number" bind:value={surroundingRadius} step={1} placeholder="Number with Step" />
                                    <div slot="right">Å</div>
                                </Input> -->
                                    <div
                                        class="horizontal-split"
                                        style="margin: 8px 0;"
                                    />
                                    <div
                                        style="color: #888BAB;margin-bottom:8px;"
                                    >
                                        Select Structures
                                    </div>
                                    <KRadioGroup
                                        value={expandFilter}
                                        on:updateValue={(e) =>
                                            (expandFilter = e.detail)}
                                    >
                                        <div
                                            class="row"
                                            style="align-items: center; justify-content: start;font-size: 12px; color: #000 !important;"
                                        >
                                            <KRadio uid={ExpandFilter.All}>
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    All
                                                </div>
                                            </KRadio>
                                        </div>
                                        <div
                                            class="row"
                                            style="align-items: center; justify-content: start;font-size: 12px;"
                                        >
                                            <KRadio uid={ExpandFilter.Residues}>
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    Residues
                                                </div>
                                            </KRadio>
                                        </div>
                                        <div
                                            class="row"
                                            style="align-items: center; justify-content: start;font-size: 12px; color: #000 !important;"
                                        >
                                            <KRadio uid={ExpandFilter.Water}>
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    Water
                                                </div>
                                            </KRadio>
                                        </div>
                                        <div
                                            class="row"
                                            style="align-items: center; justify-content: start;font-size: 12px; color: #000 !important;"
                                        >
                                            <KRadio
                                                uid={ExpandFilter.SolventWithoutWater}
                                            >
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    Solvent Other Than Water
                                                </div>
                                            </KRadio>
                                        </div>
                                        <div
                                            class="row"
                                            style="align-items: center; justify-content: start;font-size: 12px; color: #000 !important;"
                                        >
                                            <KRadio uid={ExpandFilter.Solvent}>
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    All Solvent
                                                </div>
                                            </KRadio>
                                        </div>
                                    </KRadioGroup>
                                    <div
                                        class="horizontal-split"
                                        style="margin: 8px 0"
                                    />
                                    <div
                                        style="color: #888BAB;margin-bottom:8px;"
                                    >
                                        Other Settings
                                    </div>
                                    <div
                                        class="row"
                                        style="flex-direction: column;align-items: center; justify-content: space-between;font-size: 12px; color: #000 !important;"
                                    >
                                        <KRadioGroup
                                            value={asWholeResidueState}
                                            on:updateValue={(e) =>
                                                (asWholeResidueState =
                                                    e.detail)}
                                        >
                                            <KRadio uid={1}>
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    Include full residues
                                                </div>
                                            </KRadio>
                                            <KRadio uid={0}>
                                                <div
                                                    style="color: #000 !important;"
                                                >
                                                    Include atoms
                                                </div>
                                            </KRadio>
                                        </KRadioGroup>
                                    </div>
                                    <div
                                        class="horizontal-split"
                                        style="margin: 8px 0"
                                    />
                                    <div
                                        class="row"
                                        style="align-items: center;justify-content: start;"
                                    >
                                        <KCheckbox
                                            value={excludeSelectedAtoms}
                                            on:updateValue={(e) =>
                                                (excludeSelectedAtoms =
                                                    e.detail)}
                                        >
                                            <div
                                                style="color: #000 !important;"
                                            >
                                                Exclude Selected Atoms
                                            </div>
                                        </KCheckbox>
                                    </div>
                                    <div
                                        class="row"
                                        style="align-items: center;justify-content: end;"
                                    >
                                        <Button
                                            on:click={() => {
                                                lightPlugin.managers.selection.structure.expand(
                                                    {
                                                        radius: surroundingRadius,
                                                        asWholeResidue:
                                                            asWholeResidueState,
                                                        filter: expandFilter,
                                                        excludeSelectedAtoms,
                                                    },
                                                );
                                                surroundingVisible = false;
                                                surroundingDropdownRef.handleClose();
                                            }}
                                        >
                                            <div style="color: #000000;">
                                                Confirm
                                            </div>
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </KDropdown>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Expand
                        </div>
                    </div>
                </div>
            </div>
            <div class="vertical-split" />
            <!-- Chem Assist -->
            <div style="margin: 4px 8px;">
                <div class="uni-view-horizontal-toolbar-title row">
                    Chem Assist
                </div>
                <div class="row">
                    <div class="uni-view-horizontal-toolbar-item">
                        <KDropdown
                            on:change={(e) => {
                                measureVisible = e.detail;
                            }}
                            on:command={(e) => {
                                addMeasurement(
                                    lightPlugin.managers.selection.structure
                                        .prev,
                                    e.detail,
                                );
                            }}
                            trigger="click"
                        >
                            <div
                                class="row"
                                style={"flex-shrink: 0; align-items: center; justify-content: center;"}
                            >
                                <!-- <Wrapper> -->
                                <svg
                                    style="margin-left: 5"
                                    class="normal-icon"
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 20 20"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        d="M20 0H0V20H20V0Z"
                                        fill="white"
                                        fill-opacity="0.01"
                                    />
                                    <path
                                        d="M16.9165 7.2469C17.6976 6.46585 17.6976 5.19952 16.9165 4.41847L15.5783 3.08023C14.7972 2.29918 13.5309 2.29918 12.7498 3.08023L12.6016 3.22852L11.0391 4.79102L7.91406 7.91602L4.78906 11.041L3.22656 12.6035L3.07828 12.7518C2.29723 13.5329 2.29723 14.7992 3.07828 15.5802L4.41652 16.9185C5.19757 17.6995 6.46389 17.6995 7.24494 16.9185L16.9165 7.2469Z"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="square"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M12.6016 3.22852L3.22656 12.6035"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="square"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M3.75 12.084L4.75 13.084"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M7.91406 7.91602L9.58073 9.58268"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M12.0781 3.75L13.0781 4.75"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                </svg>
                                <!-- <Tooltip>
                                    {`Pick ${pickLevelText(currGranularity)}`}
                                </Tooltip> -->
                                <!-- </Wrapper> -->
                                <svg
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 8 8"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    style={`
                                    transform: ${measureVisible ? "rotate(0)" : "rotate(180deg)"};
                                    font-size: 8px;
                                    color: #a2a5ca;
                                `}
                                >
                                    <path
                                        d="M6.95641 5.66979L4.15766 2.07713C4.07755 1.97429 3.9233 1.97429 3.84234 2.07713L1.04359 5.66979C0.939613 5.80376 1.03336 6 1.20125 6L6.79875 6C6.96664 6 7.06039 5.80376 6.95641 5.66979Z"
                                        fill="#888BAB"
                                    />
                                </svg>
                            </div>
                            <div slot="dropdown" class="menu-normal">
                                <KDropdownItem
                                    command={RepresentationType.Distance}
                                >
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <AtomIcon className={styles['normal-icon']} /> -->
                                        Distance
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem
                                    command={RepresentationType.Angle}
                                >
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ResidueIcon className={styles['normal-icon']} /> -->
                                        Angle
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem
                                    command={RepresentationType.Dihedral}
                                >
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ChainIcon className={styles['normal-icon']} /> -->
                                        Dihedral
                                    </div>
                                </KDropdownItem>
                            </div>
                        </KDropdown>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Measure
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item large">
                        <div
                            class="row"
                            style={"flex-shrink: 0; align-items: center; justify-content: center;"}
                        >
                            <svg
                                class="normal-icon"
                                style="margin-left: 5;"
                                width="1em"
                                height="1em"
                                viewBox="0 0 20 20"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                                on:click={async () => {
                                    if (interactionState) {
                                        lightPlugin.managers.cell.traverse(
                                            (cell, repr) => {
                                                if (
                                                    repr.type ===
                                                    RepresentationType.IntraInteractions
                                                ) {
                                                    lightPlugin.managers.cell.remove(
                                                        [{ ref: cell.ref }],
                                                    );
                                                }
                                            },
                                        );
                                        interactionState = false;
                                        return;
                                    }
                                    lightPlugin.managers.representation.showGlobalInteraction(
                                        undefined,
                                        "Mol3d Horizontal Toolbar Interaction",
                                    );
                                    interactionState = true;
                                }}
                            >
                                <path
                                    d="M13.3333 15.4173C13.3333 16.5679 14.2661 17.5007 15.4167 17.5007C16.5673 17.5007 17.5 16.5679 17.5 15.4173C17.5 14.2667 16.5673 13.334 15.4167 13.334C14.2661 13.334 13.3333 14.2667 13.3333 15.4173Z"
                                    stroke={interactionState
                                        ? "#6063f0"
                                        : "#A2A5C4"}
                                    stroke-width="1.3"
                                    stroke-linejoin="round"
                                />
                                <path
                                    d="M2.4974 4.58333C2.4974 5.73392 3.43015 6.66667 4.58073 6.66667C5.73131 6.66667 6.66406 5.73392 6.66406 4.58333C6.66406 3.43274 5.73131 2.5 4.58073 2.5C3.43015 2.5 2.4974 3.43274 2.4974 4.58333Z"
                                    fill={interactionState
                                        ? "#6063f0"
                                        : "#A2A5C4"}
                                    stroke={interactionState
                                        ? "#6063f0"
                                        : "#A2A5C4"}
                                    stroke-width="1.3"
                                    stroke-linejoin="round"
                                />
                                <path
                                    d="M13.3333 15.4173L5.20658 15.4173C3.71179 15.4173 2.5 14.2055 2.5 12.7107C2.5 11.2159 3.71179 10.0041 5.20658 10.0041L14.7899 10.0041C16.2867 10.0041 17.5 8.79078 17.5 7.29407C17.5 5.79732 16.2867 4.58398 14.7899 4.58398L6.66667 4.58398"
                                    stroke={interactionState
                                        ? "#6063f0"
                                        : "#A2A5C4"}
                                    stroke-width="1.3"
                                    stroke-linecap="square"
                                    stroke-linejoin="round"
                                />
                            </svg>
                            <KDropdown
                                on:change={(e) => {
                                    interactionVisible = e.detail;
                                }}
                                trigger="manual"
                                bind:this={interactionDropdownRef}
                            >
                                <svg
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 8 8"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    style={`
                                    transform: ${interactionVisible ? "rotate(0)" : "rotate(180deg)"};
                                    font-size: 8px;
                                    color: #a2a5ca;
                                `}
                                    on:click={() => {
                                        if (!interactionVisible) {
                                            interactionDropdownRef.handleOpen();
                                        } else {
                                            interactionDropdownRef.handleClose();
                                        }
                                    }}
                                >
                                    <path
                                        d="M6.95641 5.66979L4.15766 2.07713C4.07755 1.97429 3.9233 1.97429 3.84234 2.07713L1.04359 5.66979C0.939613 5.80376 1.03336 6 1.20125 6L6.79875 6C6.96664 6 7.06039 5.80376 6.95641 5.66979Z"
                                        fill="#888BAB"
                                    />
                                </svg>
                                <div slot="dropdown">
                                    <div class="interaction-setting">
                                        <div class="interaction-title">
                                            3D Interaction
                                        </div>
                                        <div class="checkbox-title">
                                            Non-covalent Bonds
                                        </div>
                                        <KCheckboxGroup
                                            value={nonCovalentBondsSetting}
                                            on:updateValue={(e) =>
                                                (nonCovalentBondsSetting =
                                                    e.detail)}
                                        >
                                            <div class="row">
                                                {#each NonCovalentBondsOption as item}
                                                    <div style="flex: 0 0 50%;">
                                                        <KCheckbox
                                                            uid={item.value}
                                                            disabled={item.disabled}
                                                        >
                                                            <div
                                                                class="row"
                                                                style="align-items: center;color: #000;"
                                                            >
                                                                <span
                                                                    style={item.disabled
                                                                        ? "color: #b1b4d3;"
                                                                        : ""}
                                                                >
                                                                    {item.label}
                                                                </span>
                                                                <div
                                                                    class="uni-view-color-block"
                                                                    style="background-color: {item.color}"
                                                                />
                                                            </div>
                                                        </KCheckbox>
                                                    </div>
                                                {/each}
                                            </div>
                                        </KCheckboxGroup>
                                        <!-- <FlowbiteCheckbox name="flavours" choices={[{
                                        value: InteractionOptions.HydrogenBonds,
                                        label: (<div>123</div>),
                                    }]} bind:group groupInputClass='ms-2'/> -->
                                        <div
                                            class="checkbox-title"
                                            style="padding-top: 8px"
                                        >
                                            Pi Interactions
                                        </div>

                                        <KCheckboxGroup
                                            value={electrostaticSetting}
                                            on:updateValue={(e) =>
                                                (electrostaticSetting =
                                                    e.detail)}
                                        >
                                            <div class="row">
                                                {#each ElectrostaticOption as item}
                                                    <div style="flex: 0 0 50%;">
                                                        <KCheckbox
                                                            uid={item.value}
                                                        >
                                                            <div
                                                                class="row"
                                                                style="align-items: center;color: #000;"
                                                            >
                                                                <span>
                                                                    {item.label}
                                                                </span>
                                                                <div
                                                                    class="uni-view-color-block"
                                                                    style="background-color: {item.color}"
                                                                />
                                                            </div>
                                                        </KCheckbox>
                                                    </div>
                                                {/each}
                                            </div>
                                        </KCheckboxGroup>
                                        <div
                                            class="checkbox-title"
                                            style="padding-top: 8px"
                                        >
                                            Object of Interaction
                                        </div>
                                        <KRadioGroup
                                            value={interactionType}
                                            on:updateValue={(e) =>
                                                (interactionType = e.detail)}
                                        >
                                            <div class="row">
                                                {#each InteractionTypeOption as item}
                                                    <div style="flex: 0 0 50%;">
                                                        <KRadio
                                                            uid={item.value}
                                                        >
                                                            <span
                                                                style="color: #000;"
                                                            >
                                                                {item.label}
                                                            </span>
                                                        </KRadio>
                                                    </div>
                                                {/each}
                                            </div>
                                        </KRadioGroup>
                                        <div class="row" style="justify-content: end;">
                                            <Button
                                                on:click={() =>
                                                    interactionDropdownRef.handleClose()}
                                            >
                                                <div style="color: #000000;margin-right: 12px;">
                                                    Cancel
                                                </div>
                                            </Button>
                                            <Button
                                                on:click={() => {
                                                    const setting = [
                                                        ...nonCovalentBondsSetting,
                                                        ...electrostaticSetting,
                                                    ];
                                                    lightPlugin.managers.representation.setInteractionParams(
                                                        setting,
                                                        interactionType,
                                                    );
                                                    interactionDropdownRef.handleClose();
                                                }}
                                            >
                                                <div style="color: #000000;">
                                                    Confirm
                                                </div></Button
                                            >
                                        </div>
                                    </div>
                                </div>
                            </KDropdown>
                        </div>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Interaction
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <KDropdown
                            on:change={(e) => {
                                labelVisible = e.detail;
                            }}
                            on:command={(e) => {
                                const { selection } =
                                    lightPlugin.managers.selection.structure;
                                const items = sliceCellItemsByGranularity(
                                    lightPlugin,
                                    Array.from(selection).map(
                                        ([ref, elementIds]) => ({
                                            ref,
                                            elementIds,
                                        }),
                                    ),
                                    e.detail,
                                );
                                if (items.length > 50) {
                                    // message.error('Please add 50 labels maximum in one time.');
                                    return;
                                }
                                addLabel(items, e.detail);
                            }}
                            trigger="click"
                        >
                            <div
                                class="row"
                                style={"flex-shrink: 0; align-items: center; justify-content: center;"}
                            >
                                <!-- <Wrapper> -->
                                <svg
                                    style="margin-left: 5"
                                    class="normal-icon"
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 20 20"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        d="M16 5.5V2.75C16 2.33579 15.6642 2 15.25 2H4.75C4.33579 2 4 2.33579 4 2.75V17L10 13.8977L16 17V15M16 7.5V13"
                                        stroke="#A2A5C4"
                                        stroke-width="1.25"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M13.5 10H18.5"
                                        stroke="#A2A5C4"
                                        stroke-width="1.25"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <line
                                        x1="6.5"
                                        y1="5.5"
                                        x2="13.5"
                                        y2="5.5"
                                        stroke="#A2A5C4"
                                        stroke-linecap="round"
                                    />
                                </svg>
                                <!-- <Tooltip>
                                    {`Pick ${pickLevelText(currGranularity)}`}
                                </Tooltip> -->
                                <!-- </Wrapper> -->
                                <svg
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 8 8"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    style={`
                                    transform: ${labelVisible ? "rotate(0)" : "rotate(180deg)"};
                                    font-size: 8px;
                                    color: #a2a5ca;
                                `}
                                >
                                    <path
                                        d="M6.95641 5.66979L4.15766 2.07713C4.07755 1.97429 3.9233 1.97429 3.84234 2.07713L1.04359 5.66979C0.939613 5.80376 1.03336 6 1.20125 6L6.79875 6C6.96664 6 7.06039 5.80376 6.95641 5.66979Z"
                                        fill="#888BAB"
                                    />
                                </svg>
                            </div>
                            <div slot="dropdown" class="menu-normal">
                                <KDropdownItem command={Granularity.Atom}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <AtomIcon className={styles['normal-icon']} /> -->
                                        Atom
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem command={Granularity.Residue}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ResidueIcon className={styles['normal-icon']} /> -->
                                        Residue
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem command={Granularity.Chain}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ChainIcon className={styles['normal-icon']} /> -->
                                        Chain
                                    </div>
                                </KDropdownItem>
                                <KDropdownItem command={Granularity.Molecular}>
                                    <div
                                        class="row"
                                        style={"align-items: center"}
                                    >
                                        <!-- <ChainIcon className={styles['normal-icon']} /> -->
                                        Molecule
                                    </div>
                                </KDropdownItem>
                            </div>
                        </KDropdown>

                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Label
                        </div>
                    </div>
                </div>
            </div>

            <div class="vertical-split" />
            <!-- Style -->
            <div style="margin: 4px 8px;">
                <div class="uni-view-horizontal-toolbar-title row">Style</div>
                <div class="row">
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={async () => {
                                if (!selectionHistory) return;
                                lightPlugin.canvas3d?.controls.setLockCameraState(
                                    true,
                                );
                                const cellItems =
                                    lightPlugin.managers.selection.structure.getSelectionCellItems();
                                const refs = await Promise.all(
                                    cellItems.map((item) =>
                                        lightPlugin.managers.representation.createOther(
                                            {
                                                data: item,
                                                type: RepresentationType.Surface,
                                                // theme: {
                                                //     transparency: {
                                                //         value: preferences.theme.transparent / 100,
                                                //     },
                                                // },
                                            },
                                        ),
                                    ),
                                );
                                setTimeout(() => {
                                    lightPlugin.canvas3d?.controls.setLockCameraState(
                                        false,
                                    );
                                }, 100);
                            }}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            width="1em"
                            height="1em"
                            viewBox="0 0 20 20"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M3 9.23453C3.58333 8.71301 5.275 7.74819 7.375 8.0611C10 8.45225 11.5 12 17 10"
                                stroke="#A2A5C4"
                            />
                            <path
                                d="M2.5 13.5C3.07971 13.034 6.26087 11.7741 8.34783 12.0537C10.1642 12.2971 11.0591 13.5663 13.5 14.5"
                                stroke="#A2A5C4"
                            />
                            <path
                                d="M5 5C6 5.32143 9 7.54286 9 9.85714C9 12.1714 7.6 14.75 7 15.5"
                                stroke="#A2A5C4"
                            />
                            <path
                                d="M11.5 5C13.0427 6.44828 15.9684 11.0241 13.5 14.5"
                                stroke="#A2A5C4"
                            />
                            <path
                                d="M2.65 15.4427V4.74213C3.78105 4.88726 6.021 5.14929 7.5 5.14929C9.51352 5.14929 10.5781 5.14911 12.6575 4.62993C13.3376 4.46011 14.253 4.41357 15.1614 4.43067C16.0225 4.44689 16.8331 4.519 17.35 4.57508V15.1497C16.7887 15.0031 16.0056 14.8086 15.2259 14.6486C14.4383 14.487 13.602 14.3493 13 14.3493C12.5298 14.3493 12.0203 14.4647 11.5269 14.6104C11.1005 14.7362 10.6448 14.8979 10.1953 15.0573C10.1203 15.0839 10.0455 15.1104 9.97108 15.1367C8.88952 15.5186 7.8699 15.85 7 15.85C5.58121 15.85 3.61073 15.5859 2.65 15.4427Z"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                                stroke-linejoin="round"
                            />
                        </svg>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Surface
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() =>
                                changeRepr(RepresentationType.Ribbon, false)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            width="1em"
                            height="1em"
                            viewBox="0 0 20 20"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M6.65625 4.99609H5.65909C4.77273 4.99609 3 5.47273 3 7.47942C3 9.4861 4.77273 9.9915 5.65909 9.9915H9.52855H13.398C14.2844 9.9915 16 10.4818 16 12.4885C16 14.4952 14.2844 14.9961 13.398 14.9961"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            />
                            <path
                                d="M11.8167 1.44141L15.5504 4.76029L11.8167 8.07918L11.8167 6.28873L6.59375 6.28873L6.59375 3.23186L11.8167 3.23186L11.8167 1.44141Z"
                                stroke="#A2A5C4"
                                stroke-width="1.25"
                                stroke-linecap="square"
                                stroke-linejoin="round"
                            />
                            <path
                                d="M9.22291 12.3613L12.9567 15.6802L9.22291 18.9991L9.22291 17.2086L4 17.2086L4 14.1518L9.22291 14.1518L9.22291 12.3613Z"
                                stroke="#A2A5C4"
                                fill="#A2A5C4"
                                stroke-width="1.25"
                                stroke-linecap="square"
                                stroke-linejoin="round"
                            />
                        </svg>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Ribbon
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() =>
                                changeRepr(RepresentationType.Line, true)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            width="1em"
                            height="1em"
                            viewBox="0 0 20 20"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M17.0938 3L3.47534 16.5704"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                                stroke-linecap="round"
                            />
                        </svg>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Line
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() =>
                                changeRepr(RepresentationType.Stick, true)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            width="1em"
                            height="1em"
                            viewBox="0 0 20 20"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <rect
                                x="14.8047"
                                y="2.57422"
                                width="3"
                                height="18"
                                rx="1.5"
                                transform="rotate(45 14.8047 2.57422)"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                        </svg>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Stick
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() =>
                                changeRepr(
                                    RepresentationType.BallAndStick,
                                    true,
                                )}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            width="1em"
                            height="1em"
                            viewBox="0 0 20 20"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <rect
                                x="13.0625"
                                y="5.7793"
                                width="1.84088"
                                height="5.56186"
                                transform="rotate(45 13.0625 5.7793)"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                            <circle
                                cx="15.5"
                                cy="4.5"
                                r="2.5"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                            <circle
                                cx="6.5"
                                cy="13.5"
                                r="4.5"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                        </svg>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Ball&Stick
                        </div>
                    </div>
                    <div class="uni-view-horizontal-toolbar-item">
                        <svg
                            on:click={() =>
                                changeRepr(RepresentationType.CPK, true)}
                            style="margin-left: 5"
                            class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                            width="1em"
                            height="1em"
                            viewBox="0 0 18 17"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M5.34928 16C2.78076 16 1 13.9853 1 11.5C1 9.01472 2.78076 7 5.34928 7C7.9178 7 10 9.01472 10 11.5C10 13.9853 7.9178 16 5.34928 16Z"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                            <circle
                                cx="8"
                                cy="6"
                                r="5"
                                transform="rotate(90 8 6)"
                                fill="#A2A5C4"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                            <path
                                d="M12.866 12C10.5829 12 9 10.2091 9 8C9 5.79086 10.5829 4 12.866 4C15.1492 4 17 5.79086 17 8C17 10.2091 15.1492 12 12.866 12Z"
                                stroke="#A2A5C4"
                                stroke-width="1.3"
                            />
                        </svg>
                        <div class="uni-view-horizontal-toolbar-subtitle">
                            CPK
                        </div>
                    </div>
                </div>
            </div>
            <div class="vertical-split" />
            <!-- 3D Control -->
            <div style="margin: 4px 8px;">
                <div class="uni-view-horizontal-toolbar-title row">
                    3D Control
                </div>
                <div class="row">
                    <div class="uni-view-horizontal-toolbar-item large">
                        <KDropdown
                            trigger="click"
                            bind:this={hydrogenDropdownRef}
                        >
                            <div>
                                <svg
                                    style="margin-left: 5"
                                    class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                                    width="1em"
                                    height="1em"
                                    viewBox="0 0 20 20"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        d="M2 6V2H6"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M6 18H2V14"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M18 14V18H14"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M14 2H18V6"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M7 5.25V14.75"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M13 5.25V14.75"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                    <path
                                        d="M7 10H13"
                                        stroke="#A2A5C4"
                                        stroke-width="1.3"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />
                                </svg>
                            </div>
                            <div slot="dropdown">
                                <div
                                    class="uni-view-horizontal-toolbar-surrounding-container"
                                    style="width: 226px"
                                >
                                    <div
                                        class="row dropdown-header"
                                        style="justify-content: space-between;align-items: center;margin-top: 4px;margin-bottom: 12px;"
                                    >
                                        <div
                                            style="line-height: 20px;height: 20px;font-weight: 600;color: #000;"
                                        >
                                            Hydrogen Display Setting
                                        </div>
                                        <div>
                                            <svg
                                                on:click={() =>
                                                    hydrogenDropdownRef.handleClose()}
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
                                                    stroke="#A2A5C4"
                                                    stroke-width="1.3"
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                />
                                            </svg>
                                        </div>
                                    </div>
                                    <div
                                        style="color: #888bab;margin-bottom: 8px;"
                                    >
                                        Polar Hydrogen
                                    </div>
                                    <KRadioGroup
                                        value={isShowPolar}
                                        on:updateValue={(e) =>
                                            (isShowPolar = e.detail)}
                                    >
                                        <KRadio uid={1}>
                                            <div style="color: #000;">Show All Polar Hydrogen</div>
                                        </KRadio>
                                        <KRadio uid={0}>
                                            <div style="color: #000;">Hide All Polar Hydrogen</div>
                                        </KRadio>
                                    </KRadioGroup>
                                    <div
                                        style="color: #888bab;margin-bottom: 8px;"
                                    >
                                        Non-polar Hydrogen
                                    </div>
                                    <KRadioGroup
                                        value={isShowNoPolar}
                                        on:updateValue={(e) =>
                                            (isShowNoPolar = e.detail)}
                                    >
                                        <KRadio uid={1}>
                                            <div style="color: #000;">
                                                Show All Non-Polar Hydrogen
                                            </div>
                                        </KRadio>
                                        <KRadio uid={0}>
                                            <div style="color: #000;">
                                                Hide All Non-Polar Hydrogen
                                            </div>
                                        </KRadio>
                                    </KRadioGroup>
                                    <div
                                        class="row"
                                        style="justify-content: end;"
                                    >
                                        <Button
                                            on:click={() => {
                                                const items =
                                                    lightPlugin.managers.selection.structure.getSelectionCellItems(
                                                        true,
                                                    );
                                                lightPlugin.managers.representation.showOrHideHs(
                                                    isShowPolar,
                                                    isShowNoPolar,
                                                    items,
                                                );
                                                hydrogenDropdownRef.handleClose();
                                            }}>
                                            <div style="color: #000;">Confirm</div></Button
                                        >
                                    </div>
                                </div>
                            </div>
                        </KDropdown>

                        <div class="uni-view-horizontal-toolbar-subtitle">
                            Hydrogen
                        </div>
                    </div>
                    <!-- <div class="uni-view-horizontal-toolbar-item">
                    <svg
                        style="margin-left: 5"
                        class="uni-view-horizontal-toolbar-icon uni-view-horizontal-toolbar-dropdown"
                        width="1em"
                        height="1em"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            d="M2.66224 21.75L6.90475 21.7501L22.4611 6.19379L18.2185 1.95117L2.66211 17.5075L2.66224 21.75Z"
                            stroke="#A2A5C4"
                            stroke-width="1.3"
                            stroke-linejoin="round"
                        />
                        <path
                            d="M13.9756 6.19336L18.2182 10.436"
                            stroke="#A2A5C4"
                            stroke-width="1.3"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        />
                    </svg>
                    <div class="uni-view-horizontal-toolbar-subtitle">Edit</div>
                </div> -->
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    [hidden] {
        display: none !important;
    }
    .row {
        display: flex;
        flex-flow: row wrap;
    }
    .uni-view-horizontal-toolbar-container {
        position: absolute;
        top: 24px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #ffffff;
        box-shadow:
            0px 6px 10px rgba(183, 192, 231, 0.1),
            0px 8px 12px 1px rgba(170, 181, 223, 0.05);
        border-radius: 4px;
        z-index: 999;
        display: flex;
        color: #000000;
    }
    .fixed-right {
        left: auto;
        right: 0;
        transform: none;
    }
    .uni-view-horizontal-toolbar-inner {
        transition: all 0.2s ease-in-out;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex-wrap: nowrap;
    }
    .uni-view-horizontal-toolbar-title {
        color: #b1b4d3;
        font-size: 8px;
        margin-bottom: 6px;
        justify-content: center;
    }
    .uni-view-horizontal-toolbar-item {
        width: 30px;
        height: 30px;
        position: relative;
    }
    .uni-view-horizontal-toolbar-item:not(:last-child) {
        margin-right: 8px;
    }
    .uni-view-horizontal-toolbar-item.large {
        width: 40px;
    }
    .uni-view-horizontal-toolbar-subtitle {
        color: #888bab;
        font-size: 8px;
        height: 12px;
        line-height: 12px;
        width: 100%;
        text-align: center;
        position: absolute;
        left: 0;
        bottom: 0;
    }
    .normal-icon {
        font-size: 16px !important;
        cursor: pointer;
        color: #a2a5c4 !important;
    }
    .uni-view-horizontal-toolbar-icon {
        margin: 0 !important;
        font-size: 16px;
        cursor: pointer;
        color: #a2a5c4 !important;
    }
    .uni-view-horizontal-toolbar-icon.disabled {
        color: #d6d8ef;
    }
    .uni-view-horizontal-toolbar-dropdown {
        width: 100%;
        height: 18px;
        text-align: center;
        position: absolute;
        left: 0;
        top: 0;
    }
    .uni-view-horizontal-toolbar-dropdown .normal-icon {
        font-size: 16px !important;
        cursor: pointer;
        color: #a2a5c4 !important;
    }
    .uni-view-horizontal-toolbar-surrounding-container {
        width: 214px;
        font-size: 12px !important;
        margin-top: 10px;
        background-color: #ffffff;
        padding: 12px;
        box-shadow:
            0px 4px 7px rgba(155, 161, 184, 0.2),
            0px 6px 10px 1px rgba(155, 161, 184, 0.1);
        border-radius: 4px;
    }
    .vertical-split {
        padding-left: 1px;
        height: 30px;
        background-color: #e9ebf7;
    }
    .horizontal-split {
        padding-top: 1px;
        background-color: #e9ebf7;
    }
    .interaction-title {
        font-size: 14px;
        font-weight: 600;
        color: #2b2e53;
        height: 20px;
        line-height: 20px;
    }
    .interaction-setting {
        background: #ffffff;
        border-radius: 4px;
        width: 360px;
        padding: 16px;
    }
    .checkbox-title {
        padding: 16px 0;
        font-size: 12px;
        color: #888bab;
    }
    .uni-view-color-block {
        width: 8px;
        height: 8px;
        border-radius: 2px;
        margin-left: 8px;
    }
</style>
