# 比值型双通道 Docking 分析报告

生成时间：自动生成 | 数据源：mutagenesis_results_merged_gpr3_f_full_20260520_0854.json (266 条) | run_label: gpr3_f_full_20260520_0854

## 1. 分析框架

PRD 定义了**双通道比值型**传感器：两个 Gpr 突变体分别偏好 ascr#18 和 ascr#3，
输出比值判别植物寄生线虫 (PPN)。核心指标：

```
sel_mut = ΔG(ascr18) − ΔG(ascr3)
  sel_mut << 0 → 偏好 ascr18 → Channel A
  sel_mut >> 0 → 偏好 ascr3  → Channel B
```

| 参数 | 值 |
|------|-----|
| 噪声 SD | 0.159 kcal/mol (Gpr2_ascr18 multiseed) |
| 3σ 显著性阈值 | 0.477 kcal/mol |
| 亲和力下限 | 5.0 kcal/mol |

### WT 基线

| 受体 | sel_wt | 天然倾向 |
|------|--------|---------|
| GprC | -0.798 | 强 ascr18 偏好 |
| Gpr2 | -0.210 | 弱 ascr18 偏好 |
| Gpr3 | 0.098 | 噪声内 |

## 2. 全谱排名（按 sel_mut 升序）

| # | 突变体 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | 通道 | 强度 | caveat |
|---|--------|------|---------|------------|-----------|------|------|--------|
| 1 | Gpr2_R59C | Gpr2 | -1.380 | -6.227 | -4.847 | A | strong |  |
| 2 | Gpr2_R59F | Gpr2 | -0.940 | -6.695 | -5.755 | A | strong |  |
| 3 | Gpr2_R59T | Gpr2 | -0.940 | -5.798 | -4.858 | A | strong |  |
| 4 | GprC_L377H | GprC | -0.928 | -6.966 | -6.038 | A | strong |  |
| 5 | Gpr2_M327A | Gpr2 | -0.921 | -6.358 | -5.437 | A | strong |  |
| 6 | Gpr2_R59D | Gpr2 | -0.915 | -5.870 | -4.955 | A | strong |  |
| 7 | GprC_L377R | GprC | -0.862 | -6.493 | -5.631 | A | strong |  |
| 8 | GprC_V91C | GprC | -0.857 | -6.874 | -6.017 | A | strong |  |
| 9 | Gpr2_R59Q | Gpr2 | -0.828 | -5.785 | -4.957 | A | strong |  |
| 10 | Gpr2_R59P | Gpr2 | -0.794 | -6.404 | -5.610 | A | strong |  |
| 11 | GprC_R174I | GprC | -0.778 | -7.012 | -6.234 | A | strong |  |
| 12 | Gpr2_R59E | Gpr2 | -0.766 | -6.404 | -5.638 | A | strong |  |
| 13 | Gpr2_M327D | Gpr2 | -0.758 | -6.736 | -5.978 | A | strong |  |
| 14 | GprC_L377A | GprC | -0.758 | -6.529 | -5.771 | A | strong | ⚠ GprC-ala |
| 15 | GprC_R174Y | GprC | -0.719 | -6.701 | -5.982 | A | strong |  |
| 16 | Gpr2_M327R | Gpr2 | -0.698 | -6.679 | -5.981 | A | strong |  |
| 17 | Gpr3_R167D | Gpr3 | -0.688 | -5.599 | -4.911 | A | strong |  |
| 18 | Gpr2_Y200A | Gpr2 | -0.683 | -7.183 | -6.500 | A | strong |  |
| 19 | Gpr2_R59W | Gpr2 | -0.681 | -6.132 | -5.451 | A | strong |  |
| 20 | GprC_Q411T | GprC | -0.673 | -7.143 | -6.470 | A | strong |  |
| 21 | GprC_Q411R | GprC | -0.658 | -7.072 | -6.414 | A | strong |  |
| 22 | GprC_L377I | GprC | -0.643 | -6.826 | -6.183 | A | strong |  |
| 23 | Gpr3_D100Q | Gpr3 | -0.642 | -5.135 | -4.493 | A | strong |  |
| 24 | GprC_V91D | GprC | -0.627 | -6.963 | -6.336 | A | strong |  |
| 25 | GprC_V91P | GprC | -0.620 | -6.848 | -6.228 | A | strong |  |
| 26 | GprC_V91Q | GprC | -0.599 | -6.993 | -6.394 | A | strong |  |
| 27 | GprC_V91M | GprC | -0.591 | -7.028 | -6.437 | A | strong |  |
| 28 | GprC_V91L | GprC | -0.588 | -6.917 | -6.329 | A | strong |  |
| 29 | Gpr2_R59S | Gpr2 | -0.573 | -5.755 | -5.182 | A | strong |  |
| 30 | Gpr2_M327W | Gpr2 | -0.570 | -7.408 | -6.838 | A | strong |  |
| 31 | Gpr2_R59H | Gpr2 | -0.567 | -6.059 | -5.492 | A | strong |  |
| 32 | Gpr2_R59V | Gpr2 | -0.550 | -5.655 | -5.105 | A | strong |  |
| 33 | GprC_L377T | GprC | -0.516 | -7.461 | -6.945 | A | strong |  |
| 34 | Gpr3_R167F | Gpr3 | -0.503 | -5.737 | -5.234 | A | strong |  |
| 35 | GprC_R174G | GprC | -0.503 | -6.506 | -6.003 | A | strong |  |
| 36 | GprC_L377K | GprC | -0.498 | -6.652 | -6.154 | A | strong |  |
| 37 | GprC_R174V | GprC | -0.492 | -6.740 | -6.248 | A | strong |  |
| 38 | Gpr3_F170S | Gpr3 | -0.477 | -4.934 | -4.457 | neutral | strong |  |
| 39 | GprC_Q411D | GprC | -0.466 | -6.799 | -6.333 | neutral | moderate |  |
| 40 | GprC_V91E | GprC | -0.462 | -6.836 | -6.374 | neutral | moderate |  |
| 41 | Gpr3_F170A | Gpr3 | -0.446 | -4.941 | -4.495 | neutral | moderate |  |
| 42 | GprC_R174F | GprC | -0.439 | -6.634 | -6.195 | neutral | moderate |  |
| 43 | Gpr2_R59K | Gpr2 | -0.438 | -6.372 | -5.934 | neutral | moderate |  |
| 44 | GprC_R395A | GprC | -0.428 | -6.146 | -5.718 | neutral | moderate | ⚠ GprC-ala |
| 45 | GprC_R174P | GprC | -0.427 | -6.774 | -6.347 | neutral | moderate |  |
| 46 | Gpr2_R59L | Gpr2 | -0.425 | -6.052 | -5.627 | neutral | moderate |  |
| 47 | GprC_L377C | GprC | -0.414 | -6.330 | -5.916 | neutral | moderate |  |
| 48 | Gpr3_I141H | Gpr3 | -0.411 | -5.699 | -5.288 | neutral | moderate |  |
| 49 | GprC_R174A | GprC | -0.406 | -6.629 | -6.223 | neutral | moderate | ⚠ GprC-ala |
| 50 | GprC_Q411N | GprC | -0.406 | -6.742 | -6.336 | neutral | moderate |  |
| 51 | Gpr2_R59Y | Gpr2 | -0.405 | -6.146 | -5.741 | neutral | moderate |  |
| 52 | GprC_V91I | GprC | -0.404 | -7.196 | -6.792 | neutral | moderate |  |
| 53 | GprC_N60A | GprC | -0.402 | -6.800 | -6.398 | neutral | moderate | ⚠ GprC-ala |
| 54 | Gpr3_V138Q | Gpr3 | -0.400 | -4.943 | -4.543 | neutral | moderate |  |
| 55 | Gpr2_M327H | Gpr2 | -0.399 | -5.606 | -5.207 | neutral | moderate |  |
| 56 | GprC_V91K | GprC | -0.386 | -6.837 | -6.451 | neutral | moderate |  |
| 57 | GprC_V91F | GprC | -0.383 | -6.869 | -6.486 | neutral | moderate |  |
| 58 | Gpr2_M327E | Gpr2 | -0.375 | -5.576 | -5.201 | neutral | moderate |  |
| 59 | GprC_L377F | GprC | -0.375 | -7.334 | -6.959 | neutral | moderate |  |
| 60 | GprC_V91R | GprC | -0.360 | -6.839 | -6.479 | neutral | moderate |  |
| 61 | GprC_V91S | GprC | -0.359 | -6.753 | -6.394 | neutral | moderate |  |
| 62 | Gpr3_V138K | Gpr3 | -0.358 | -3.283 | -2.925 | neutral | moderate |  |
| 63 | Gpr2_M327N | Gpr2 | -0.357 | -6.186 | -5.829 | neutral | moderate |  |
| 64 | Gpr2_T124A | Gpr2 | -0.353 | -6.035 | -5.682 | neutral | moderate |  |
| 65 | Gpr2_R59A | Gpr2 | -0.351 | -6.569 | -6.218 | neutral | moderate |  |
| 66 | GprC_R174C | GprC | -0.337 | -6.604 | -6.267 | neutral | moderate |  |
| 67 | Gpr2_K326A | Gpr2 | -0.327 | -5.877 | -5.550 | neutral | moderate |  |
| 68 | GprC_N378V | GprC | -0.326 | -6.303 | -5.977 | neutral | moderate |  |
| 69 | GprC_Q411W | GprC | -0.316 | -6.700 | -6.384 | neutral | moderate |  |
| 70 | Gpr2_R59M | Gpr2 | -0.313 | -5.601 | -5.288 | neutral | moderate |  |
| 71 | GprC_L377Y | GprC | -0.312 | -6.800 | -6.488 | neutral | moderate |  |
| 72 | GprC_R174S | GprC | -0.310 | -6.541 | -6.231 | neutral | moderate |  |
| 73 | Gpr2_M327F | Gpr2 | -0.307 | -5.549 | -5.242 | neutral | moderate |  |
| 74 | Gpr3_D100P | Gpr3 | -0.305 | -3.086 | -2.781 | neutral | moderate |  |
| 75 | Gpr3_D100E | Gpr3 | -0.300 | -4.591 | -4.291 | neutral | moderate |  |
| 76 | Gpr3_D100S | Gpr3 | -0.285 | -5.848 | -5.563 | neutral | moderate |  |
| 77 | GprC_V91G | GprC | -0.284 | -7.070 | -6.786 | neutral | moderate |  |
| 78 | Gpr2_M327V | Gpr2 | -0.281 | -5.916 | -5.635 | neutral | moderate |  |
| 79 | GprC_R174K | GprC | -0.271 | -6.727 | -6.456 | neutral | moderate |  |
| 80 | Gpr2_M327Y | Gpr2 | -0.267 | -5.759 | -5.492 | neutral | moderate |  |
| 81 | Gpr2_N381A | Gpr2 | -0.265 | -5.812 | -5.547 | neutral | moderate |  |
| 82 | GprC_L377E | GprC | -0.257 | -6.573 | -6.316 | neutral | moderate |  |
| 83 | GprC_L377V | GprC | -0.257 | -5.976 | -5.719 | neutral | moderate |  |
| 84 | GprC_R174E | GprC | -0.255 | -6.403 | -6.148 | neutral | moderate |  |
| 85 | GprC_N378F | GprC | -0.253 | -6.583 | -6.330 | neutral | moderate |  |
| 86 | Gpr3_R164L | Gpr3 | -0.231 | -5.036 | -4.805 | neutral | moderate |  |
| 87 | Gpr2_M327P | Gpr2 | -0.230 | -5.885 | -5.655 | neutral | moderate |  |
| 88 | GprC_R174Q | GprC | -0.225 | -6.701 | -6.476 | neutral | moderate |  |
| 89 | GprC_Q411M | GprC | -0.222 | -7.185 | -6.963 | neutral | moderate |  |
| 90 | GprC_Q411E | GprC | -0.210 | -6.574 | -6.364 | neutral | moderate |  |
| 91 | GprC_R174D | GprC | -0.200 | -6.398 | -6.198 | neutral | moderate |  |
| 92 | GprC_N378R | GprC | -0.194 | -6.492 | -6.298 | neutral | moderate |  |
| 93 | Gpr3_R164I | Gpr3 | -0.193 | -5.578 | -5.385 | neutral | moderate |  |
| 94 | Gpr3_F170H | Gpr3 | -0.193 | -5.624 | -5.431 | neutral | moderate |  |
| 95 | Gpr3_D100Y | Gpr3 | -0.193 | -5.294 | -5.101 | neutral | moderate |  |
| 96 | GprC_Q411G | GprC | -0.193 | -7.157 | -6.964 | neutral | moderate |  |
| 97 | GprC_L377D | GprC | -0.191 | -6.617 | -6.426 | neutral | moderate |  |
| 98 | Gpr3_D100A | Gpr3 | -0.185 | -5.612 | -5.427 | neutral | moderate |  |
| 99 | Gpr3_D100T | Gpr3 | -0.179 | -5.926 | -5.747 | neutral | moderate |  |
| 100 | Gpr2_M327C | Gpr2 | -0.178 | -6.240 | -6.062 | neutral | moderate |  |
| 101 | GprC_N378I | GprC | -0.177 | -6.882 | -6.705 | neutral | moderate |  |
| 102 | GprC_R174L | GprC | -0.174 | -6.430 | -6.256 | neutral | moderate |  |
| 103 | Gpr3_D100F | Gpr3 | -0.172 | -2.906 | -2.734 | neutral | moderate |  |
| 104 | Gpr3_R167L | Gpr3 | -0.169 | -3.178 | -3.009 | neutral | moderate |  |
| 105 | Gpr3_I141S | Gpr3 | -0.167 | -5.615 | -5.448 | neutral | moderate |  |
| 106 | GprC_Q411H | GprC | -0.163 | -7.064 | -6.901 | neutral | moderate |  |
| 107 | GprC_V91Y | GprC | -0.154 | -6.359 | -6.205 | neutral | noise |  |
| 108 | Gpr3_F170N | Gpr3 | -0.148 | -3.157 | -3.009 | neutral | noise |  |
| 109 | Gpr3_R175A | Gpr3 | -0.148 | -4.665 | -4.517 | neutral | noise |  |
| 110 | Gpr3_V138L | Gpr3 | -0.143 | -3.226 | -3.083 | neutral | noise |  |
| 111 | GprC_L377M | GprC | -0.132 | -6.646 | -6.514 | neutral | noise |  |
| 112 | Gpr3_F170Y | Gpr3 | -0.130 | -5.162 | -5.032 | neutral | noise |  |
| 113 | Gpr3_I141C | Gpr3 | -0.129 | -2.955 | -2.826 | neutral | noise |  |
| 114 | Gpr3_V138H | Gpr3 | -0.129 | -5.640 | -5.511 | neutral | noise |  |
| 115 | GprC_R174T | GprC | -0.127 | -6.098 | -5.971 | neutral | noise |  |
| 116 | GprC_N378W | GprC | -0.125 | -6.977 | -6.852 | neutral | noise |  |
| 117 | GprC_V91W | GprC | -0.118 | -7.127 | -7.009 | neutral | noise |  |
| 118 | GprC_L377W | GprC | -0.117 | -6.595 | -6.478 | neutral | noise |  |
| 119 | Gpr3_V138N | Gpr3 | -0.111 | -3.129 | -3.018 | neutral | noise |  |
| 120 | Gpr3_R167S | Gpr3 | -0.108 | -5.112 | -5.004 | neutral | noise |  |
| 121 | Gpr3_F170T | Gpr3 | -0.106 | -4.584 | -4.478 | neutral | noise |  |
| 122 | GprC_H189A | GprC | -0.104 | -6.830 | -6.726 | neutral | noise | ⚠ GprC-ala |
| 123 | GprC_N378C | GprC | -0.099 | -6.909 | -6.810 | neutral | noise |  |
| 124 | Gpr3_F170V | Gpr3 | -0.096 | -5.152 | -5.056 | neutral | noise |  |
| 125 | Gpr3_V138D | Gpr3 | -0.091 | -3.093 | -3.002 | neutral | noise |  |
| 126 | Gpr3_R167N | Gpr3 | -0.090 | -3.113 | -3.023 | neutral | noise |  |
| 127 | Gpr3_I141F | Gpr3 | -0.087 | -3.000 | -2.913 | neutral | noise |  |
| 128 | GprC_N378H | GprC | -0.077 | -7.219 | -7.142 | neutral | noise |  |
| 129 | Gpr3_R167I | Gpr3 | -0.076 | -5.304 | -5.228 | neutral | noise |  |
| 130 | Gpr3_N171A | Gpr3 | -0.074 | -5.625 | -5.551 | neutral | noise |  |
| 131 | GprC_V91T | GprC | -0.068 | -7.038 | -6.970 | neutral | noise |  |
| 132 | Gpr3_D100H | Gpr3 | -0.068 | -4.787 | -4.719 | neutral | noise |  |
| 133 | Gpr3_R164H | Gpr3 | -0.064 | -3.064 | -3.000 | neutral | noise |  |
| 134 | Gpr3_I141P | Gpr3 | -0.058 | -5.299 | -5.241 | neutral | noise |  |
| 135 | Gpr3_I141N | Gpr3 | -0.054 | -3.110 | -3.056 | neutral | noise |  |
| 136 | GprC_V91H | GprC | -0.051 | -6.867 | -6.816 | neutral | noise |  |
| 137 | Gpr2_M327T | Gpr2 | -0.050 | -6.084 | -6.034 | neutral | noise |  |
| 138 | Gpr3_I141R | Gpr3 | -0.050 | -3.069 | -3.019 | neutral | noise |  |
| 139 | GprC_Q411F | GprC | -0.049 | -6.567 | -6.518 | neutral | noise |  |
| 140 | Gpr3_R164C | Gpr3 | -0.040 | -2.811 | -2.771 | neutral | noise |  |
| 141 | Gpr3_F170D | Gpr3 | -0.035 | -5.147 | -5.112 | neutral | noise |  |
| 142 | Gpr3_F170E | Gpr3 | -0.032 | -5.341 | -5.309 | neutral | noise |  |
| 143 | GprC_R174H | GprC | -0.026 | -6.159 | -6.133 | neutral | noise |  |
| 144 | Gpr2_M327I | Gpr2 | -0.024 | -5.999 | -5.975 | neutral | noise |  |
| 145 | Gpr3_V138T | Gpr3 | -0.024 | -3.027 | -3.003 | neutral | noise |  |
| 146 | Gpr3_D100G | Gpr3 | -0.024 | -5.361 | -5.337 | neutral | noise |  |
| 147 | Gpr3_F170Q | Gpr3 | -0.022 | -5.527 | -5.505 | neutral | noise |  |
| 148 | Gpr3_V138S | Gpr3 | -0.021 | -3.048 | -3.027 | neutral | noise |  |
| 149 | Gpr3_D100K | Gpr3 | -0.021 | -4.387 | -4.366 | neutral | noise |  |
| 150 | Gpr3_R167G | Gpr3 | -0.012 | -2.877 | -2.865 | neutral | noise |  |
| 151 | Gpr3_I141A | Gpr3 | -0.006 | -2.983 | -2.977 | neutral | noise |  |
| 152 | Gpr3_V138R | Gpr3 | -0.006 | -2.980 | -2.974 | neutral | noise |  |
| 153 | GprC_R174M | GprC | 0.009 | -6.531 | -6.540 | neutral | noise |  |
| 154 | Gpr3_I141M | Gpr3 | 0.017 | -2.973 | -2.990 | neutral | noise |  |
| 155 | Gpr3_I141L | Gpr3 | 0.019 | -3.043 | -3.062 | neutral | noise |  |
| 156 | Gpr3_F170I | Gpr3 | 0.030 | -4.526 | -4.556 | neutral | noise |  |
| 157 | Gpr3_R164V | Gpr3 | 0.032 | -2.853 | -2.885 | neutral | noise |  |
| 158 | Gpr3_I141D | Gpr3 | 0.033 | -2.900 | -2.933 | neutral | noise |  |
| 159 | Gpr3_F170R | Gpr3 | 0.034 | -5.384 | -5.418 | neutral | noise |  |
| 160 | GprC_Q411C | GprC | 0.034 | -6.927 | -6.961 | neutral | noise |  |
| 161 | Gpr3_V138G | Gpr3 | 0.037 | -3.025 | -3.062 | neutral | noise |  |
| 162 | GprC_L377P | GprC | 0.039 | -6.011 | -6.050 | neutral | noise |  |
| 163 | Gpr3_Q93A | Gpr3 | 0.041 | -5.984 | -6.025 | neutral | noise |  |
| 164 | GprC_N378P | GprC | 0.043 | -6.407 | -6.450 | neutral | noise |  |
| 165 | Gpr3_R164K | Gpr3 | 0.046 | -2.882 | -2.928 | neutral | noise |  |
| 166 | GprC_L377N | GprC | 0.053 | -6.117 | -6.170 | neutral | noise |  |
| 167 | Gpr2_R59G | Gpr2 | 0.055 | -5.798 | -5.853 | neutral | noise |  |
| 168 | Gpr2_Y330A | Gpr2 | 0.058 | -6.349 | -6.407 | neutral | noise |  |
| 169 | Gpr3_V138I | Gpr3 | 0.063 | -5.186 | -5.249 | neutral | noise |  |
| 170 | Gpr2_R59N | Gpr2 | 0.064 | -5.683 | -5.747 | neutral | noise |  |
| 171 | Gpr3_R164T | Gpr3 | 0.080 | -2.708 | -2.788 | neutral | noise |  |
| 172 | GprC_L377G | GprC | 0.081 | -6.325 | -6.406 | neutral | noise |  |
| 173 | Gpr3_R167H | Gpr3 | 0.085 | -4.729 | -4.814 | neutral | noise |  |
| 174 | GprC_N378T | GprC | 0.085 | -6.269 | -6.354 | neutral | noise |  |
| 175 | Gpr3_F170C | Gpr3 | 0.087 | -2.835 | -2.922 | neutral | noise |  |
| 176 | Gpr3_F170P | Gpr3 | 0.088 | -2.944 | -3.032 | neutral | noise |  |
| 177 | Gpr3_F170M | Gpr3 | 0.089 | -4.967 | -5.056 | neutral | noise |  |
| 178 | Gpr3_D100C | Gpr3 | 0.097 | -3.086 | -3.183 | neutral | noise |  |
| 179 | Gpr2_M327L | Gpr2 | 0.097 | -5.382 | -5.479 | neutral | noise |  |
| 180 | Gpr3_I141Q | Gpr3 | 0.099 | -2.891 | -2.990 | neutral | noise |  |
| 181 | Gpr3_R164F | Gpr3 | 0.104 | -5.138 | -5.242 | neutral | noise |  |
| 182 | GprC_N378L | GprC | 0.104 | -6.741 | -6.845 | neutral | noise |  |
| 183 | Gpr3_I141K | Gpr3 | 0.108 | -2.897 | -3.005 | neutral | noise |  |
| 184 | Gpr3_R167V | Gpr3 | 0.109 | -5.292 | -5.401 | neutral | noise |  |
| 185 | Gpr2_M327G | Gpr2 | 0.110 | -5.608 | -5.718 | neutral | noise |  |
| 186 | GprC_V91N | GprC | 0.112 | -7.136 | -7.248 | neutral | noise |  |
| 187 | Gpr3_V138E | Gpr3 | 0.115 | -2.930 | -3.045 | neutral | noise |  |
| 188 | GprC_N378D | GprC | 0.118 | -6.897 | -7.015 | neutral | noise |  |
| 189 | Gpr3_V138F | Gpr3 | 0.118 | -2.837 | -2.955 | neutral | noise |  |
| 190 | Gpr3_V138C | Gpr3 | 0.120 | -5.685 | -5.805 | neutral | noise |  |
| 191 | GprC_N378Q | GprC | 0.120 | -6.837 | -6.957 | neutral | noise |  |
| 192 | GprC_Q411Y | GprC | 0.120 | -6.942 | -7.062 | neutral | noise |  |
| 193 | Gpr3_R167K | Gpr3 | 0.122 | -4.715 | -4.837 | neutral | noise |  |
| 194 | Gpr2_Y378A | Gpr2 | 0.127 | -5.493 | -5.620 | neutral | noise |  |
| 195 | Gpr3_F170W | Gpr3 | 0.128 | -5.807 | -5.935 | neutral | noise |  |
| 196 | GprC_N378E | GprC | 0.129 | -7.250 | -7.379 | neutral | noise |  |
| 197 | Gpr3_R167E | Gpr3 | 0.129 | -2.918 | -3.047 | neutral | noise |  |
| 198 | Gpr2_M327Q | Gpr2 | 0.130 | -5.668 | -5.798 | neutral | noise |  |
| 199 | Gpr3_R164E | Gpr3 | 0.131 | -2.612 | -2.743 | neutral | noise |  |
| 200 | Gpr3_D100R | Gpr3 | 0.132 | -4.290 | -4.422 | neutral | noise |  |
| 201 | Gpr3_D100V | Gpr3 | 0.138 | -4.303 | -4.441 | neutral | noise |  |
| 202 | GprC_Q411K | GprC | 0.138 | -6.791 | -6.929 | neutral | noise |  |
| 203 | Gpr3_D100N | Gpr3 | 0.139 | -4.386 | -4.525 | neutral | noise |  |
| 204 | Gpr2_I63A | Gpr2 | 0.143 | -6.180 | -6.323 | neutral | noise |  |
| 205 | Gpr3_R167Q | Gpr3 | 0.150 | -5.206 | -5.356 | neutral | noise |  |
| 206 | Gpr2_I120A | Gpr2 | 0.151 | -5.950 | -6.101 | neutral | noise |  |
| 207 | Gpr3_V138P | Gpr3 | 0.158 | -2.836 | -2.994 | neutral | noise |  |
| 208 | GprC_Q411V | GprC | 0.159 | -7.113 | -7.272 | neutral | noise |  |
| 209 | Gpr2_M327S | Gpr2 | 0.160 | -6.045 | -6.205 | neutral | moderate |  |
| 210 | Gpr3_D100M | Gpr3 | 0.162 | -4.663 | -4.825 | neutral | moderate |  |
| 211 | Gpr3_D100L | Gpr3 | 0.168 | -4.250 | -4.418 | neutral | moderate |  |
| 212 | Gpr3_D100I | Gpr3 | 0.169 | -4.286 | -4.455 | neutral | moderate |  |
| 213 | Gpr3_I141W | Gpr3 | 0.180 | -4.690 | -4.870 | neutral | moderate |  |
| 214 | GprC_Q411I | GprC | 0.190 | -7.073 | -7.263 | neutral | moderate |  |
| 215 | GprC_Y185A | GprC | 0.192 | -6.383 | -6.575 | neutral | moderate | ⚠ GprC-ala |
| 216 | GprC_R174W | GprC | 0.192 | -6.265 | -6.457 | neutral | moderate |  |
| 217 | GprC_Q415A | GprC | 0.201 | -6.495 | -6.696 | neutral | moderate | ⚠ GprC-ala |
| 218 | GprC_Q411P | GprC | 0.214 | -6.832 | -7.046 | neutral | moderate |  |
| 219 | Gpr3_V138Y | Gpr3 | 0.219 | -4.700 | -4.919 | neutral | moderate |  |
| 220 | Gpr3_F170K | Gpr3 | 0.220 | -5.061 | -5.281 | neutral | moderate |  |
| 221 | Gpr3_R164D | Gpr3 | 0.225 | -2.639 | -2.864 | neutral | moderate |  |
| 222 | GprC_N378K | GprC | 0.227 | -7.028 | -7.255 | neutral | moderate |  |
| 223 | Gpr3_R164P | Gpr3 | 0.228 | -2.565 | -2.793 | neutral | moderate |  |
| 224 | GprC_S44A | GprC | 0.234 | -6.278 | -6.512 | neutral | moderate | ⚠ GprC-ala |
| 225 | Gpr3_R167W | Gpr3 | 0.239 | -5.674 | -5.913 | neutral | moderate |  |
| 226 | GprC_N378S | GprC | 0.239 | -7.124 | -7.363 | neutral | moderate |  |
| 227 | Gpr3_R164S | Gpr3 | 0.265 | -4.639 | -4.904 | neutral | moderate |  |
| 228 | GprC_Q411L | GprC | 0.271 | -7.044 | -7.315 | neutral | moderate |  |
| 229 | GprC_L377Q | GprC | 0.277 | -6.269 | -6.546 | neutral | moderate |  |
| 230 | Gpr3_I141V | Gpr3 | 0.283 | -5.326 | -5.609 | neutral | moderate |  |
| 231 | GprC_N378Y | GprC | 0.307 | -6.133 | -6.440 | neutral | moderate |  |
| 232 | Gpr2_R59I | Gpr2 | 0.319 | -5.530 | -5.849 | neutral | moderate |  |
| 233 | Gpr3_I141Y | Gpr3 | 0.333 | -2.550 | -2.883 | neutral | moderate |  |
| 234 | GprC_N56A | GprC | 0.341 | -5.579 | -5.920 | neutral | moderate | ⚠ GprC-ala |
| 235 | Gpr3_V138A | Gpr3 | 0.342 | -4.644 | -4.986 | neutral | moderate |  |
| 236 | Gpr3_I141T | Gpr3 | 0.346 | -5.579 | -5.925 | neutral | moderate |  |
| 237 | Gpr3_R164N | Gpr3 | 0.348 | -2.549 | -2.897 | neutral | moderate |  |
| 238 | GprC_N378G | GprC | 0.364 | -6.520 | -6.884 | neutral | moderate |  |
| 239 | Gpr3_I141G | Gpr3 | 0.372 | -5.617 | -5.989 | neutral | moderate |  |
| 240 | Gpr3_R167M | Gpr3 | 0.379 | -4.679 | -5.058 | neutral | moderate |  |
| 241 | Gpr3_R167T | Gpr3 | 0.397 | -3.267 | -3.664 | neutral | moderate |  |
| 242 | GprC_Y425A | GprC | 0.421 | -6.002 | -6.423 | neutral | moderate | ⚠ GprC-ala |
| 243 | GprC_P381A | GprC | 0.423 | -6.042 | -6.465 | neutral | moderate | ⚠ GprC-ala |
| 244 | Gpr3_R164W | Gpr3 | 0.424 | -4.667 | -5.091 | neutral | moderate |  |
| 245 | Gpr3_R164Y | Gpr3 | 0.444 | -4.705 | -5.149 | neutral | moderate |  |
| 246 | GprC_N378M | GprC | 0.473 | -6.476 | -6.949 | neutral | moderate |  |
| 247 | Gpr3_I141E | Gpr3 | 0.477 | -4.543 | -5.020 | neutral | moderate |  |
| 248 | GprC_R174N | GprC | 0.485 | -6.135 | -6.620 | B | strong |  |
| 249 | Gpr3_R164G | Gpr3 | 0.495 | -4.600 | -5.095 | B | strong |  |
| 250 | Gpr3_R164Q | Gpr3 | 0.495 | -4.584 | -5.079 | B | strong |  |
| 251 | GprC_V91A | GprC | 0.525 | -7.479 | -8.004 | B | strong | ⚠ GprC-ala |
| 252 | Gpr3_D100W | Gpr3 | 0.528 | -4.456 | -4.984 | neutral | strong |  |
| 253 | Gpr3_V138W | Gpr3 | 0.528 | -3.159 | -3.687 | neutral | strong |  |
| 254 | Gpr3_F170L | Gpr3 | 0.620 | -4.698 | -5.318 | B | strong |  |
| 255 | Gpr2_M327K | Gpr2 | 0.644 | -4.951 | -5.595 | B | strong |  |
| 256 | GprC_Q411A | GprC | 0.652 | -5.530 | -6.182 | B | strong | ⚠ GprC-ala |
| 257 | Gpr3_F170G | Gpr3 | 0.659 | -4.309 | -4.968 | neutral | strong |  |
| 258 | Gpr3_I178A | Gpr3 | 0.673 | -4.714 | -5.387 | B | strong |  |
| 259 | Gpr3_R164M | Gpr3 | 0.679 | -4.609 | -5.288 | B | strong |  |
| 260 | GprC_L377S | GprC | 0.684 | -5.894 | -6.578 | B | strong |  |
| 261 | Gpr3_R167C | Gpr3 | 0.712 | -4.610 | -5.322 | B | strong |  |
| 262 | GprC_Q411S | GprC | 0.759 | -5.333 | -6.092 | B | strong |  |
| 263 | Gpr3_R167P | Gpr3 | 0.812 | -4.850 | -5.662 | B | strong |  |
| 264 | Gpr3_V138M | Gpr3 | 0.838 | -4.657 | -5.495 | B | strong |  |
| 265 | Gpr3_R167Y | Gpr3 | 0.906 | -4.809 | -5.715 | B | strong |  |
| 266 | GprC_N378A | GprC | 0.957 | -5.385 | -6.342 | B | strong | ⚠ GprC-ala |

## 3. Channel A 候选（ascr18 偏好，sel_mut < −0.477）

### 3a. 无 caveat

| # | 突变体 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | ΔΔG(ascr18) |
|---|--------|------|---------|------------|-----------|-------------|
| 1 | Gpr2_R59C | Gpr2 | -1.380 | -6.227 | -4.847 | -0.416 |
| 2 | Gpr2_R59F | Gpr2 | -0.940 | -6.695 | -5.755 | -0.884 |
| 3 | Gpr2_R59T | Gpr2 | -0.940 | -5.798 | -4.858 | 0.013 |
| 4 | GprC_L377H | GprC | -0.928 | -6.966 | -6.038 | 1.309 |
| 5 | Gpr2_M327A | Gpr2 | -0.921 | -6.358 | -5.437 | -0.547 |
| 6 | Gpr2_R59D | Gpr2 | -0.915 | -5.870 | -4.955 | -0.059 |
| 7 | GprC_L377R | GprC | -0.862 | -6.493 | -5.631 | 1.782 |
| 8 | GprC_V91C | GprC | -0.857 | -6.874 | -6.017 | 1.401 |
| 9 | Gpr2_R59Q | Gpr2 | -0.828 | -5.785 | -4.957 | 0.026 |
| 10 | Gpr2_R59P | Gpr2 | -0.794 | -6.404 | -5.610 | -0.593 |
| 11 | GprC_R174I | GprC | -0.778 | -7.012 | -6.234 | 1.263 |
| 12 | Gpr2_R59E | Gpr2 | -0.766 | -6.404 | -5.638 | -0.593 |
| 13 | Gpr2_M327D | Gpr2 | -0.758 | -6.736 | -5.978 | -0.925 |
| 14 | GprC_R174Y | GprC | -0.719 | -6.701 | -5.982 | 1.574 |
| 15 | Gpr2_M327R | Gpr2 | -0.698 | -6.679 | -5.981 | -0.868 |
| 16 | Gpr3_R167D | Gpr3 | -0.688 | -5.599 | -4.911 | 0.129 |
| 17 | Gpr2_Y200A | Gpr2 | -0.683 | -7.183 | -6.500 | -1.372 |
| 18 | Gpr2_R59W | Gpr2 | -0.681 | -6.132 | -5.451 | -0.321 |
| 19 | GprC_Q411T | GprC | -0.673 | -7.143 | -6.470 | 1.132 |
| 20 | GprC_Q411R | GprC | -0.658 | -7.072 | -6.414 | 1.203 |
| 21 | GprC_L377I | GprC | -0.643 | -6.826 | -6.183 | 1.449 |
| 22 | Gpr3_D100Q | Gpr3 | -0.642 | -5.135 | -4.493 | 0.593 |
| 23 | GprC_V91D | GprC | -0.627 | -6.963 | -6.336 | 1.312 |
| 24 | GprC_V91P | GprC | -0.620 | -6.848 | -6.228 | 1.427 |
| 25 | GprC_V91Q | GprC | -0.599 | -6.993 | -6.394 | 1.282 |
| 26 | GprC_V91M | GprC | -0.591 | -7.028 | -6.437 | 1.247 |
| 27 | GprC_V91L | GprC | -0.588 | -6.917 | -6.329 | 1.358 |
| 28 | Gpr2_R59S | Gpr2 | -0.573 | -5.755 | -5.182 | 0.056 |
| 29 | Gpr2_M327W | Gpr2 | -0.570 | -7.408 | -6.838 | -1.597 |
| 30 | Gpr2_R59H | Gpr2 | -0.567 | -6.059 | -5.492 | -0.248 |
| 31 | Gpr2_R59V | Gpr2 | -0.550 | -5.655 | -5.105 | 0.156 |
| 32 | GprC_L377T | GprC | -0.516 | -7.461 | -6.945 | 0.814 |
| 33 | Gpr3_R167F | Gpr3 | -0.503 | -5.737 | -5.234 | -0.009 |
| 34 | GprC_R174G | GprC | -0.503 | -6.506 | -6.003 | 1.769 |
| 35 | GprC_L377K | GprC | -0.498 | -6.652 | -6.154 | 1.623 |
| 36 | GprC_R174V | GprC | -0.492 | -6.740 | -6.248 | 1.535 |

### 3b. GprC alanine scan（⚠ caveat）

| # | 突变体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | ΔΔG(ascr18) | ΔΔG(ascr3) |
|---|--------|---------|------------|-----------|-------------|-------------|
| 1 | GprC_L377A | -0.758 | -6.529 | -5.771 | 1.746 | 1.706 |

## 4. Channel B 候选（ascr3 偏好，sel_mut > +0.477）

### 4a. 无 caveat

| # | 突变体 | 受体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | ΔΔG(ascr3) |
|---|--------|------|---------|-----------|------------|-------------|
| 1 | GprC_R174N | GprC | 0.485 | -6.620 | -6.135 | 0.857 |
| 2 | Gpr3_R164G | Gpr3 | 0.495 | -5.095 | -4.600 | 0.731 |
| 3 | Gpr3_R164Q | Gpr3 | 0.495 | -5.079 | -4.584 | 0.747 |
| 4 | Gpr3_F170L | Gpr3 | 0.620 | -5.318 | -4.698 | 0.508 |
| 5 | Gpr2_M327K | Gpr2 | 0.644 | -5.595 | -4.951 | 0.006 |
| 6 | Gpr3_I178A | Gpr3 | 0.673 | -5.387 | -4.714 | 0.439 |
| 7 | Gpr3_R164M | Gpr3 | 0.679 | -5.288 | -4.609 | 0.538 |
| 8 | GprC_L377S | GprC | 0.684 | -6.578 | -5.894 | 0.899 |
| 9 | Gpr3_R167C | Gpr3 | 0.712 | -5.322 | -4.610 | 0.504 |
| 10 | GprC_Q411S | GprC | 0.759 | -6.092 | -5.333 | 1.385 |
| 11 | Gpr3_R167P | Gpr3 | 0.812 | -5.662 | -4.850 | 0.164 |
| 12 | Gpr3_V138M | Gpr3 | 0.838 | -5.495 | -4.657 | 0.331 |
| 13 | Gpr3_R167Y | Gpr3 | 0.906 | -5.715 | -4.809 | 0.111 |

### 4b. GprC alanine scan（⚠ caveat：差异化破坏副产品，非真正选择性工程）

| # | 突变体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | ΔΔG(ascr18) | ΔΔG(ascr3) |
|---|--------|---------|-----------|------------|-------------|-------------|
| 1 | GprC_V91A | 0.525 | -8.004 | -7.479 | 0.796 | -0.527 |
| 2 | GprC_Q411A | 0.652 | -6.182 | -5.530 | 2.745 | 1.295 |
| 3 | GprC_N378A | 0.957 | -6.342 | -5.385 | 2.890 | 1.135 |

## 5. 跨受体配对排名

D = sel_A − sel_B（越负 = 判别力越强）

balance = |sel_A| / (|sel_A| + |sel_B|)（理想 = 0.5）

### 5a. 无 caveat 配对 Top 10

| # | Channel A | Channel B | D | balance | sel_A | sel_B | ΔG_A(ascr18) | ΔG_B(ascr3) |
|---|-----------|-----------|---|---------|-------|-------|--------------|-------------|
| 1 | Gpr2_R59C | Gpr3_R167Y | -2.286 | 0.604 | -1.380 | 0.906 | -6.227 | -5.715 |
| 2 | Gpr2_R59C | Gpr3_V138M | -2.218 | 0.622 | -1.380 | 0.838 | -6.227 | -5.495 |
| 3 | Gpr2_R59C | Gpr3_R167P | -2.192 | 0.630 | -1.380 | 0.812 | -6.227 | -5.662 |
| 4 | Gpr2_R59C | GprC_Q411S | -2.139 | 0.645 | -1.380 | 0.759 | -6.227 | -6.092 |
| 5 | Gpr2_R59C | Gpr3_R167C | -2.092 | 0.660 | -1.380 | 0.712 | -6.227 | -5.322 |
| 6 | Gpr2_R59C | GprC_L377S | -2.064 | 0.669 | -1.380 | 0.684 | -6.227 | -6.578 |
| 7 | Gpr2_R59C | Gpr3_R164M | -2.059 | 0.670 | -1.380 | 0.679 | -6.227 | -5.288 |
| 8 | Gpr2_R59C | Gpr3_I178A | -2.053 | 0.672 | -1.380 | 0.673 | -6.227 | -5.387 |
| 9 | Gpr2_R59C | Gpr3_F170L | -2.000 | 0.690 | -1.380 | 0.620 | -6.227 | -5.318 |
| 10 | Gpr2_R59C | Gpr3_R164G | -1.875 | 0.736 | -1.380 | 0.495 | -6.227 | -5.095 |

### 5b. 含 GprC-ala caveat 配对 Top 10（仅供参考，不直接进入湿实验推荐）

| # | Channel A | Channel B | D | balance | sel_A | sel_B | caveat |
|---|-----------|-----------|---|---------|-------|-------|--------|
| 1 | Gpr2_R59C | GprC_N378A | -2.337 | 0.591 | -1.380 | 0.957 | ⚠ GprC-ala |
| 2 | Gpr2_R59C | GprC_Q411A | -2.032 | 0.679 | -1.380 | 0.652 | ⚠ GprC-ala |
| 3 | Gpr2_R59C | GprC_V91A | -1.905 | 0.724 | -1.380 | 0.525 | ⚠ GprC-ala |
| 4 | Gpr2_R59F | GprC_N378A | -1.897 | 0.496 | -0.940 | 0.957 | ⚠ GprC-ala |
| 5 | Gpr2_R59T | GprC_N378A | -1.897 | 0.496 | -0.940 | 0.957 | ⚠ GprC-ala |
| 6 | Gpr2_M327A | GprC_N378A | -1.878 | 0.490 | -0.921 | 0.957 | ⚠ GprC-ala |
| 7 | Gpr2_R59D | GprC_N378A | -1.872 | 0.489 | -0.915 | 0.957 | ⚠ GprC-ala |
| 8 | Gpr2_R59Q | GprC_N378A | -1.785 | 0.464 | -0.828 | 0.957 | ⚠ GprC-ala |
| 9 | Gpr2_R59P | GprC_N378A | -1.751 | 0.453 | -0.794 | 0.957 | ⚠ GprC-ala |
| 10 | Gpr2_R59E | GprC_N378A | -1.723 | 0.445 | -0.766 | 0.957 | ⚠ GprC-ala |

## 6. 湿实验配对建议

基于无 caveat 跨受体配对 Top 3：

1. **Gpr2_R59C** (Channel A, sel=-1.380) + **Gpr3_R167Y** (Channel B, sel=0.906)
   - D = -2.286, balance = 0.604
   - 亲和力：A端 ΔG(ascr18) = -6.227, B端 ΔG(ascr3) = -5.715

2. **Gpr2_R59C** (Channel A, sel=-1.380) + **Gpr3_V138M** (Channel B, sel=0.838)
   - D = -2.218, balance = 0.622
   - 亲和力：A端 ΔG(ascr18) = -6.227, B端 ΔG(ascr3) = -5.495

3. **Gpr2_R59C** (Channel A, sel=-1.380) + **Gpr3_R167P** (Channel B, sel=0.812)
   - D = -2.192, balance = 0.630
   - 亲和力：A端 ΔG(ascr18) = -6.227, B端 ΔG(ascr3) = -5.662

## 7. 边界与 caveat

1. **GprC alanine scan caveat**：GprC 13/14 个 Ala 突变体显示非特异性结合破坏（ΔΔG(ascr18) 常 >2 kcal/mol），产生的表观 ascr3 偏好是差异化破坏副产品，不代表真正的选择性工程。这些候选须经 saturation scan 验证后才可进入湿实验。
2. **噪声阈值**：基于 Gpr2_ascr18 multiseed SD=0.159，这是系统中最大的 SD，作为保守估计。|sel_mut| < 0.477 的选择性差异不可靠。
3. **刚性对接局限**：AutoDock Vina 刚性对接不考虑蛋白柔性和溶剂效应，ΔG 绝对值仅作相对排名参考，不代表真实结合自由能。
4. **亲和力下限**：Channel 候选要求 |ΔG| ≥ 5.0 kcal/mol，确保突变体仍有足够结合力激活信号通路。参照系统最弱 WT = Gpr3_ascr18 = −5.726。

## 附录：统计摘要

| 类别 | 数量 |
|------|------|
| 总突变数 | 266 |
| Channel A 无 caveat | 36 |
| Channel A 含 GprC-ala caveat | 1 |
| Channel B 无 caveat | 13 |
| Channel B 含 GprC-ala caveat | 3 |
| 中性区 | 213 |
| 跨受体配对 (无 caveat) | 374 |
| 跨受体配对 (含 caveat) | 57 |
