<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import type { LoadingStatus } from "@gradio/statustracker";
    import fileSelector from './utils/fileSelector';
    import { Textarea, Button, Toast } from 'flowbite-svelte';
    import { fastaCheck } from "./utils/string";
    import "./flowbite-svelte.css";
    import "./index.less";
    import "./smui-dark.css";

    const example = `> Chain A

DFPHVKDEIKRVFGDNSKQTGENLKFHDPLYQLKLKFTYAGGKSGVGITANMLVDHNRSKGIDMQFNQYNLGVGHTQNGNTVFDKEYSEELNGTRFKIKDTISAFLNAFVDNAKDPYINDGNFNTYTSSVAFMLIRAGVHPDWIISFIGQPVLRELADFTQRYESKIIPKEDVGKSSFDIIVEKYETINQESYKDAESRAFSLDTLQESIEVGVHGIDLDVLKTFKGFQEQAKRLNESVQLS`

	export let gradio: Gradio<{
		change: never;
		submit: never;
		input: never;
		clear_status: LoadingStatus;
	}>;
	export let value = "";
	export let submit;

	// When the value changes, dispatch the change event via handle_change()
	// See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive

    let sequence = '';
    const importFasta = async () => {
        fileSelector.setAttrs({ accept: `.fasta` });
        const fileList = await fileSelector.selectFile();
        const file = fileList.item(0);
        if (!file) return;
        const res = await file.text();
        sequence = res;
    }
    let errorMsg = '';
</script>

<div class="sequence-input-container">
    {#if !!errorMsg}
        <Toast toastStatus={true}>
            {errorMsg}
        </Toast>
    {/if}
    <Textarea class="dark:bg-gray-700" style="box-shadow: none;border: 0 !important;width: 100%;height: 100%;min-height: 240px;overflow-x: auto;border: none;resize: none !important;z-index: 1;position:relative;" bind:value={sequence} placeholder={example} />
    
    <div class="sequence-input-toolbar row w-full bg-gray-50 dark:bg-gray-700 text-gray-900 dark:placeholder-gray-400 dark:text-white border dark:border-gray-600 p-2.5 text-sm focus:ring-primary-500 border-gray-300 focus:border-primary-500 dark:focus:ring-primary-500 dark:focus:border-primary-500 disabled:cursor-not-allowed disabled:opacity-50" style="justify-content: space-between;align-items: center;">
        <div class="row">
            <Button style="padding: 0.625rem 1.25rem !important;margin-right: 8px;" class="text-center font-medium focus-within:ring-4 focus-within:outline-none inline-flex items-center justify-center px-3 py-2 text-xs text-white bg-primary-700 hover:bg-primary-800 dark:bg-primary-600 dark:hover:bg-primary-700 focus-within:ring-primary-300 dark:focus-within:ring-primary-800 rounded-lg sequence-input-toolbar-btn" size="xs" on:click={() => importFasta()}>Import .fasta</Button>
            <Button style="padding: 0.625rem 1.25rem !important;" class="text-center font-medium focus-within:ring-4 focus-within:outline-none inline-flex items-center justify-center px-3 py-2 text-xs text-white bg-primary-700 hover:bg-primary-800 dark:bg-primary-600 dark:hover:bg-primary-700 focus-within:ring-primary-300 dark:focus-within:ring-primary-800 rounded-lg sequence-input-toolbar-btn" size="xs" on:click={() => sequence = example}>Example</Button>
        </div>
        <div class="row">
            <Button style="padding: 0.625rem 1.25rem !important;margin-right: 8px;" class="text-center font-medium focus-within:ring-4 focus-within:outline-none inline-flex items-center justify-center px-3 py-2 text-xs text-white bg-primary-700 hover:bg-primary-800 dark:bg-primary-600 dark:hover:bg-primary-700 focus-within:ring-primary-300 dark:focus-within:ring-primary-800 rounded-lg sequence-input-toolbar-btn" size="xs" on:click={() => sequence = ''}>Clear</Button>
            <Button style="padding: 0.625rem 1.25rem !important;" class="text-center font-medium focus-within:ring-4 focus-within:outline-none inline-flex items-center justify-center px-3 py-2 text-xs text-white bg-primary-700 hover:bg-primary-800 dark:bg-primary-600 dark:hover:bg-primary-700 focus-within:ring-primary-300 dark:focus-within:ring-primary-800 rounded-lg sequence-input-toolbar-btn" size="xs" disabled={!sequence} on:click={() => {
                const isCorrect = fastaCheck(sequence);
                if (isCorrect !== 0) {
                    errorMsg = isCorrect === 1
                            ? 'Please enter the correct header information.'
                            : 'Please enter the correct sequence information.';
                    return;
                }
                errorMsg = '';
                submit(sequence)
                sequence = '';
            }}>
                Input Sequence
            </Button>
        </div>
    </div>
</div>

<style>
    .sequence-input-container {
        position: relative;
        border: 1px solid #E9EBF7;
        padding: 12px 12px 56px 12px;
        border-radius: 12px;
    }
    .sequence-textarea {
        width: 100%;
        height: 100%;
        overflow-x: auto;
        border: none;
        resize: none !important;
    }

    .sequence-input-toolbar {
        width: calc(100% - 24px);
        position: absolute;
        bottom: 9px;
        left: 0;
        padding: 6px 12px;
        border: 0 !important;
        margin: 0 12px;
    }
    .row {
        display: flex;
        flex-flow: row wrap;
    }
</style>
