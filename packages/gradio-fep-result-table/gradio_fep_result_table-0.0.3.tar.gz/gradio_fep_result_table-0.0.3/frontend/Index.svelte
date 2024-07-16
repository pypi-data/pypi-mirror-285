<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { BlockTitle } from "@gradio/atoms";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { tick } from "svelte";
	import './index.css';
	import { KImage } from '@ikun-ui/image';
	import DataTable, { Row, Cell, Head, Body } from '@smui/data-table';

	export let gradio: Gradio<{
		change: never;
		submit: never;
		input: never;
		clear_status: LoadingStatus;
	}>;
	export let label = "Textbox";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value = "";
	export let placeholder = "";
	export let show_label: boolean;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus | undefined = undefined;
	export let value_is_output = false;
	export let interactive: boolean;
	export let rtl = false;
	export let max_height;
	window.process = {
		env: {
			NODE_ENV: 'production',
			LANG: '',
		}
	}

	let el: HTMLTextAreaElement | HTMLInputElement;
	const container = true;

	function handle_change(): void {
		gradio.dispatch("change");
		if (!value_is_output) {
			gradio.dispatch("input");
		}
	}

	async function handle_keypress(e: KeyboardEvent): Promise<void> {
		await tick();
		if (e.key === "Enter") {
			e.preventDefault();
			gradio.dispatch("submit");
		}
	}

	const headers = ["LigandA", "LigandB", "Predicted ddG", "Leg", "Replicas", "Overlap", "Free Energy", "Exchange Traj", "ddG vs Lambda Pairs"];

	const ligandImg = new Map();
	let tableData = [];
	let idToPair = new Map();

	const updateValue = () => {
		const checkboxes = document.querySelectorAll(
			'input[name="fep_result_checkbox"]:checked',
		);
		let res = [];
		checkboxes.forEach((checkbox) => {
			res.push(idToPair.get(checkbox.value));
		});
		value = JSON.stringify({ res })
	}

	const init = () => {
		const { ligands, pairs } = JSON.parse(placeholder);
		console.log(ligands)
		ligands.forEach(item => {
			ligandImg.set(item.name, item.img);
		});
		tableData = pairs.map((item, index) => {
			const key = `${item.ligand_a}_${item.ligand_b}_${index}`;
			idToPair.set(key, { ligandA: item.ligand_a, ligandB: item.ligand_b })
			return {
				...item,
				key,
			};
		});
		console.log(max_height);
	}
	$: if (value === null) value = "";

	// When the value changes, dispatch the change event via handle_change()
	// See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive
	$: value, handle_change();

	$: placeholder, init();
</script>

<Block
	{visible}
	{elem_id}
	{elem_classes}
	{scale}
	{min_width}
	allow_overflow={false}
	padding={true}
>
	<!-- <DataTable>
		<Head>
			<Row>
				<Cell>Select</Cell>
				{#each headers as header}
					<Cell>{header}</Cell>
				{/each}
			</Row>
		</Head>
		<Body style={`max-height: ${max_height}px; overflow-y: auto;`}>
			{#each tableData as data}
				<Row>
					<Cell rowspan={2}><input type='checkbox' name='fep_result_checkbox' value={data.key} on:change={updateValue} /></Cell>
					<Cell rowspan={2} class="fep-result-img">
						<KImage class="fep-result-img"  src='{ligandImg.get(data['ligand_a'])}' previewSrcList={[ligandImg.get(data['ligand_a'])]} prop />
						{data['ligand_a']}
					</Cell>
					<Cell rowspan={2} class="fep-result-img">
						<KImage   src='{ligandImg.get(data.ligand_b)}' previewSrcList={[ligandImg.get(data.ligand_b)]} />
						{data['ligand_b']}
					</Cell>
					<Cell rowspan={2}>{(+data['pred_ddg']).toFixed(3)} ± {(+data['pred_ddg_err']).toFixed(3)}</Cell>
					<Cell>{data.leg_info[0]['leg']}</Cell>
					<Cell class="fep-result-img"><KImage  src={data.leg_info[0]['replicas']} previewSrcList={[data.leg_info[0]['replicas']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src={data.leg_info[0]['overlap']} previewSrcList={[data.leg_info[0]['overlap']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src={data.leg_info[0]['free_energy']} previewSrcList={[data.leg_info[0]['free_energy']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src={data.leg_info[0]['exchange_traj']} previewSrcList={[data.leg_info[0]['exchange_traj']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src={data.leg_info[0]['ddG_vs_lambda_pairs']} previewSrcList={[data.leg_info[0]['ddG_vs_lambda_pairs']]} /></Cell>
				</Row>
				<Row>
					<Cell>{data.leg_info[1]['leg']}</Cell>
					<Cell class="fep-result-img"><KImage  src='{data.leg_info[1]['replicas']}' previewSrcList={[data.leg_info[1]['replicas']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src='{data.leg_info[1]['overlap']}' previewSrcList={[data.leg_info[1]['overlap']]} /></Cell>
					<Cell class="fep-result-img"><KImage src='{data.leg_info[1]['free_energy']}' previewSrcList={[data.leg_info[1]['free_energy']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src='{data.leg_info[1]['exchange_traj']}' previewSrcList={[data.leg_info[1]['exchange_traj']]} /></Cell>
					<Cell class="fep-result-img"><KImage  src='{data.leg_info[1]['ddG_vs_lambda_pairs']}' previewSrcList={[data.leg_info[1]['ddG_vs_lambda_pairs']]} /></Cell>
				</Row>
			{/each}
		</Body>
	</DataTable> -->
	<table border='1' class="fep-result-table" style={`max-height: ${max_height}px`}>
		<thead>
			<tr>
				<th>Select</th>
				{#each headers as header}
					<th>{header}</th>
				{/each}
			</tr>
		</thead>
		<tbody class="fep-result-table-body">
			{#each tableData as data}
				<tr>
					<td rowspan='2'><input type='checkbox' name='fep_result_checkbox' value={data.key} on:change={updateValue} /></td>
					<td rowspan='2' class="fep-result-img">
						<KImage class="fep-result-img"  src='{ligandImg.get(data['ligand_a'])}' previewSrcList={[ligandImg.get(data['ligand_a'])]} prop />
						{data['ligand_a']}
					</td>
					<td rowspan='2' class="fep-result-img">
						<KImage   src='{ligandImg.get(data.ligand_b)}' previewSrcList={[ligandImg.get(data.ligand_b)]} />
						{data['ligand_b']}
					</td>
					<td rowspan='2'>{(+data['pred_ddg']).toFixed(3)} ± {(+data['pred_ddg_err']).toFixed(3)}</td>
					<td>{data.leg_info[0]['leg']}</td>
					<td class="fep-result-img"><KImage  src={data.leg_info[0]['replicas']} previewSrcList={[data.leg_info[0]['replicas']]} /></td>
					<td class="fep-result-img"><KImage  src={data.leg_info[0]['overlap']} previewSrcList={[data.leg_info[0]['overlap']]} /></td>
					<td class="fep-result-img"><KImage  src={data.leg_info[0]['free_energy']} previewSrcList={[data.leg_info[0]['free_energy']]} /></td>
					<td class="fep-result-img"><KImage  src={data.leg_info[0]['exchange_traj']} previewSrcList={[data.leg_info[0]['exchange_traj']]} /></td>
					<td class="fep-result-img"><KImage  src={data.leg_info[0]['ddG_vs_lambda_pairs']} previewSrcList={[data.leg_info[0]['ddG_vs_lambda_pairs']]} /></td>
				</tr>
				<tr>
					<td>{data.leg_info[1]['leg']}</td>
					<td class="fep-result-img"><KImage  src='{data.leg_info[1]['replicas']}' previewSrcList={[data.leg_info[1]['replicas']]} /></td>
					<td class="fep-result-img"><KImage  src='{data.leg_info[1]['overlap']}' previewSrcList={[data.leg_info[1]['overlap']]} /></td>
					<td class="fep-result-img"><KImage src='{data.leg_info[1]['free_energy']}' previewSrcList={[data.leg_info[1]['free_energy']]} /></td>
					<td class="fep-result-img"><KImage  src='{data.leg_info[1]['exchange_traj']}' previewSrcList={[data.leg_info[1]['exchange_traj']]} /></td>
					<td class="fep-result-img"><KImage  src='{data.leg_info[1]['ddG_vs_lambda_pairs']}' previewSrcList={[data.leg_info[1]['ddG_vs_lambda_pairs']]} /></td>
				</tr>
			{/each}
		</tbody>
	</table>
</Block>

<style>
	label {
		display: block;
		width: 100%;
	}

	input {
		display: block;
		position: relative;
		outline: none !important;
		box-shadow: var(--input-shadow);
		padding: var(--input-padding);
		width: 100%;
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		border: none;
		border-radius: 4px;
		color: #555878;
		background: #f2f5fa;
		border-color: light-dark(rgb(118, 118, 118), rgb(133, 133, 133));
	}
	.container > input {
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
	}
	input:disabled {
		-webkit-text-fill-color: var(--body-text-color);
		-webkit-opacity: 1;
		opacity: 1;
	}
	input:focus {
		box-shadow: var(--input-shadow-focus);
		border-color: var(--input-border-color-focus);
	}

	input::placeholder {
		color: var(--input-placeholder-color);
	}

	input:checked {
		background: #6063f0;
		color: #fff;
	}

	.fep-result-table {
		background: #fff;
		color: #000;
		border-color: #000;
		width: 100%;
		overflow: auto;
		display: block;
	}

	.fep-result-table-body {
		overflow: auto;
	}

	.fep-result-img {
		width: 100px;
    	height: 100px;
	}

	tr, td {
		border-width: 1px !important;
	}
	td {
		text-align: center;
	}
</style>
