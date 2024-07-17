<svelte:options accessors={true} />

<script lang="ts">
    import type { Gradio } from "@gradio/utils";
    import type { LoadingStatus } from "@gradio/statustracker";
    import "./index.css";
    import "./index.less";
    import "./flowbite-svelte.css";
    import { RepresentationType } from "dpmol";

    export let gradio: Gradio<{
        change: never;
        submit: never;
        input: never;
        clear_status: LoadingStatus;
    }>;
    export let lightPlugin;
</script>

<div class="uni-view-vertical-toolbar-container">
    <div class="uni-view-vertical-toolbar-wrapper">
        <div class="uni-view-vertical-toolbar-subtitle">View</div>
        <!-- ZoomIn -->
        <svg
            on:click={() => lightPlugin.managers.camera.zoomIn()}
            class="uni-view-vertical-toolbar-icon"
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
        <!-- ZoomOut -->
        <svg
            on:click={() => lightPlugin.managers.camera.zoomOut()}
            class="uni-view-vertical-toolbar-icon"
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
        <!-- Focus -->
        <svg
            on:click={() => lightPlugin.managers.camera.focus()}
            class="uni-view-vertical-toolbar-icon"
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
    </div>
    <div class="uni-view-vertical-toolbar-horizontal-split" />
    <div class="uni-view-vertical-toolbar-wrapper">
        <div class="uni-view-vertical-toolbar-subtitle">Show</div>
        <svg
            on:click={() =>
                lightPlugin.toggle({ types: [RepresentationType.Label] })}
            class="uni-view-vertical-toolbar-icon"
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
        <svg
            on:click={() =>
                lightPlugin.toggle({
                    types: [
                        RepresentationType.Distance,
                        RepresentationType.Angle,
                        RepresentationType.Dihedral,
                    ],
                })}
            class="uni-view-vertical-toolbar-icon"
            width="1em"
            height="1em"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path d="M20 0H0V20H20V0Z" fill="white" fillOpacity="0.01" />
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
        <svg
            on:click={() =>
                lightPlugin.toggle({
                    types: [RepresentationType.Ribbon],
                })}
            class="uni-view-vertical-toolbar-icon"
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
        <svg
            on:click={() =>
                lightPlugin.toggle({
                    types: [RepresentationType.Surface],
                })}
            class="uni-view-vertical-toolbar-icon"
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
    </div>
    <!--  -->
</div>

<style>
    .uni-view-vertical-toolbar-container {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 999;
        width: 34px;
        background: #ffffff;
        border-radius: 4px;
        padding: 0 6px;
        box-shadow:
            0px 6px 10px rgba(183, 192, 231, 0.1),
            0px 8px 12px 1px rgba(170, 181, 223, 0.05);
    }
    .uni-view-vertical-toolbar-wrapper {
        padding: 12px 3px;
        display: flex;
        flex-direction: column;
    }
    .uni-view-vertical-toolbar-subtitle {
        color: #b1b4d3;
        font-size: 8px;
        height: 12px;
        width: 18px;
        margin-bottom: 6px;
        position: relative;
        left: -1px;
    }
    .uni-view-vertical-toolbar-icon {
        margin-top: 6px;
        margin-bottom: 6px;
        font-size: 16px;
        cursor: pointer;
        color: #a2a5c4 !important;
    }
    .uni-view-vertical-toolbar-icon.disabled {
        color: #d6d8ef;
    }
    .uni-view-vertical-toolbar-icon:last-child {
        margin-bottom: 0;
    }
    .uni-view-vertical-toolbar-horizontal-split {
        padding-top: 1px;
        background-color: #e9ebf7;
    }
</style>
