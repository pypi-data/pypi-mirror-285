<svelte:options accessors={true} />

<script lang="ts">
    import type { Gradio } from "@gradio/utils";
    import type { LoadingStatus } from "@gradio/statustracker";

    const ElementsPeriodicData = [
        [
            [1, "H", "#ECD3FB", "#BA5CF1"],
            [-1],
            [-11],
            [-12],
            [-13],
            [-14],
            [-15],
            [-15],
            [-17],
            [-18],
            [-19],
            [-110],
            [-111],
            [-112],
            [-113],
            [-114],
            [-115],
            [2, "He", "#FAE2CB", "#ED913A"],
        ],
        [
            [3, "Li", "#ECD3FB", "#BA5CF1"],
            [4, "Be", "#D3DEFB", "#5680EE"],
            [-21],
            [-22],
            [-23],
            [-24],
            [-25],
            [-26],
            [-27],
            [-28],
            [-29],
            [-210],
            [5, "B", "#C1EBF8", "#3BBAE0"],
            [6, "C", "#C1EBF8", "#3BBAE0"],
            [7, "N", "#C1EBF8", "#3BBAE0"],
            [8, "O", "#C1EBF8", "#3BBAE0"],
            [9, "F", "#C1EBF8", "#3BBAE0"],
            [10, "Ne", "#FAE2CB", "#ED913A"],
        ],
        [
            [11, "Na", "#ECD3FB", "#BA5CF1"],
            [12, "Mg", "#D3DEFB", "#5680EE"],
            [-31],
            [-32],
            [-33],
            [-34],
            [-35],
            [-36],
            [-37],
            [-38],
            [-39],
            [-310],
            [13, "Al", "#C1EBF8", "#3BBAE0"],
            [14, "Si", "#C1EBF8", "#3BBAE0"],
            [15, "P", "#C1EBF8", "#3BBAE0"],
            [16, "S", "#C1EBF8", "#3BBAE0"],
            [17, "Cl", "#C1EBF8", "#3BBAE0"],
            [18, "Ar", "#FAE2CB", "#ED913A"],
        ],
        [
            [19, "K", "#ECD3FB", "#BA5CF1"],
            [20, "Ca", "#D3DEFB", "#5680EE"],
            [21, "Sc", "#D3E7FB", "#60AAF0"],
            [22, "Ti", "#D3E7FB", "#60AAF0"],
            [23, "V", "#D3E7FB", "#60AAF0"],
            [24, "Cr", "#D3E7FB", "#60AAF0"],
            [25, "Mn", "#D3E7FB", "#60AAF0"],
            [26, "Fe", "#D3E7FB", "#60AAF0"],
            [27, "Co", "#D3E7FB", "#60AAF0"],
            [28, "Ni", "#D3E7FB", "#60AAF0"],
            [29, "Cu", "#D3E7FB", "#60AAF0"],
            [30, "Zn", "#D3E7FB", "#60AAF0"],
            [31, "Ga", "#C1EBF8", "#3BBAE0"],
            [32, "Ge", "#C1EBF8", "#3BBAE0"],
            [33, "As", "#C1EBF8", "#3BBAE0"],
            [34, "Se", "#C1EBF8", "#3BBAE0"],
            [35, "Br", "#C1EBF8", "#3BBAE0"],
            [36, "Kr", "#FAE2CB", "#ED913A"],
        ],
        [
            [37, "Rb", "#ECD3FB", "#BA5CF1"],
            [38, "Sr", "#D3DEFB", "#5680EE"],
            [39, "Y", "#D3E7FB", "#60AAF0"],
            [40, "Zr", "#D3E7FB", "#60AAF0"],
            [41, "Nb", "#D3E7FB", "#60AAF0"],
            [42, "Mo", "#D3E7FB", "#60AAF0"],
            [43, "Tc", "#D3E7FB", "#60AAF0"],
            [44, "Ru", "#D3E7FB", "#60AAF0"],
            [45, "Rh", "#D3E7FB", "#60AAF0"],
            [46, "Pd", "#D3E7FB", "#60AAF0"],
            [47, "Ag", "#D3E7FB", "#60AAF0"],
            [48, "Cd", "#D3E7FB", "#60AAF0"],
            [49, "In", "#C1EBF8", "#3BBAE0"],
            [50, "Sn", "#C1EBF8", "#3BBAE0"],
            [51, "Sb", "#C1EBF8", "#3BBAE0"],
            [52, "Te", "#C1EBF8", "#3BBAE0"],
            [53, "I", "#C1EBF8", "#3BBAE0"],
            [54, "Xe", "#FAE2CB", "#ED913A"],
        ],
        [
            [55, "Cs", "#ECD3FB", "#BA5CF1"],
            [56, "Ba", "#D3DEFB", "#5680EE"],
            [57, "La", "#C8F5F4", "#24D1CE"],
            [72, "Hf", "#D3E7FB", "#60AAF0"],
            [73, "Ta", "#D3E7FB", "#60AAF0"],
            [74, "W", "#D3E7FB", "#60AAF0"],
            [75, "Re", "#D3E7FB", "#60AAF0"],
            [76, "Os", "#D3E7FB", "#60AAF0"],
            [77, "Ir", "#D3E7FB", "#60AAF0"],
            [78, "Pt", "#D3E7FB", "#60AAF0"],
            [79, "Au", "#D3E7FB", "#60AAF0"],
            [80, "Hg", "#D3E7FB", "#60AAF0"],
            [81, "Tl", "#C1EBF8", "#3BBAE0"],
            [82, "Pb", "#C1EBF8", "#3BBAE0"],
            [83, "Bi", "#C1EBF8", "#3BBAE0"],
            [84, "Po", "#C1EBF8", "#3BBAE0"],
            [85, "At", "#C1EBF8", "#3BBAE0"],
            [86, "Rn", "#FAE2CB", "#ED913A"],
        ],
        [
            [87, "Fr", "#ECD3FB", "#BA5CF1"],
            [88, "Ra", "#D3DEFB", "#5680EE"],
            [89, "Ac", "#C8F5F4", "#24D1CE"],
        ],
        [
            [-81],
            [-82],
            [58, "Ce", "#C8F5F4", "#24D1CE"],
            [59, "Pr", "#C8F5F4", "#24D1CE"],
            [60, "Nd", "#C8F5F4", "#24D1CE"],
            [61, "Pm", "#C8F5F4", "#24D1CE"],
            [62, "Sm", "#C8F5F4", "#24D1CE"],
            [63, "Eu", "#C8F5F4", "#24D1CE"],
            [64, "Gd", "#C8F5F4", "#24D1CE"],
            [65, "Tb", "#C8F5F4", "#24D1CE"],
            [66, "Dy", "#C8F5F4", "#24D1CE"],
            [67, "Ho", "#C8F5F4", "#24D1CE"],
            [68, "Er", "#C8F5F4", "#24D1CE"],
            [69, "Tm", "#C8F5F4", "#24D1CE"],
            [70, "Yb", "#C8F5F4", "#24D1CE"],
            [71, "Lu", "#C8F5F4", "#24D1CE"],
        ],
        [
            [-91],
            [-92],
            [90, "Th", "#C8F5F4", "#24D1CE"],
            [91, "Pa", "#C8F5F4", "#24D1CE"],
            [92, "U", "#C8F5F4", "#24D1CE"],
            [93, "Np", "#C8F5F4", "#24D1CE"],
            [94, "Pu", "#C8F5F4", "#24D1CE"],
            [95, "Am", "#C8F5F4", "#24D1CE"],
            [96, "Cm", "#C8F5F4", "#24D1CE"],
            [97, "Bk", "#C8F5F4", "#24D1CE"],
            [98, "Cf", "#C8F5F4", "#24D1CE"],
            [99, "Es", "#C8F5F4", "#24D1CE"],
            [100, "Fm", "#C8F5F4", "#24D1CE"],
            [101, "Md", "#C8F5F4", "#24D1CE"],
            [102, "No", "#C8F5F4", "#24D1CE"],
            [103, "Lr", "#C8F5F4", "#24D1CE"],
        ],
    ];
    export let gradio: Gradio<{
        change: never;
        submit: never;
        input: never;
        clear_status: LoadingStatus;
    }>;
    export let onClick;
</script>

<div>
    {#each ElementsPeriodicData as row}
        <div class="row">
            {#each row as ele, eleIndex}
                {#if +ele[0] < 0}
                    <div class="ele-wrap-empty" />
                {/if}
                {#if !(+ele[0] < 0)}
                    <div
                        class="ele-wrap"
                        style="background-color: {ele[2]};margin-right: {eleIndex !==
                        row.length - 1
                            ? 2
                            : 0}px;"
                        on:click={() =>
                            onClick({ atomNo: ele[0], atomLabel: ele[1] })}
                    >
                        <span class="ele-label">{ele[1]}</span>
                        <span class="ele-number" style="color: {ele[3]} !important">
                            {ele[0]}
                        </span>
                    </div>
                {/if}
            {/each}
        </div>
    {/each}
</div>

<style>
    .row {
        display: flex;
        flex-flow: row wrap;
    }

    .ele-wrap {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        position: relative;
        margin-bottom: 2px;
        margin-right: 2px;
        cursor: pointer;
    }
    .ele-wrap:hover {
        background-color: #6063f0 !important;
    }
    .ele-wrap:hover .ele-number{
        color: #ffffff !important;
    }
    .ele-wrap:hover .ele-label {
        color: #ffffff !important;
    }
    .ele-wrap-empty {
        width: 32px;
        height: 32px;
        margin-bottom: 2px;
        margin-right: 2px;
    }
    .ele-number {
        position: absolute;
        top: 0;
        right: 4px;
        height: 14px;
        line-height: 14px;
        font-size: 10px;
    }
    .ele-label {
        position: absolute;
        left: 4px;
        bottom: 0px;
        height: 24px;
        line-height: 24px;
        font-size: 16px;
        color: #555878 !important;
    }
</style>
