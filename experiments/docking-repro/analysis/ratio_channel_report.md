# 比值型双通道 Docking 分析报告

生成时间：自动生成 | 数据源：mutagenesis_results_merged_20260416.json (212 条)

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
| Gpr2 | -0.404 | 弱 ascr18 偏好 |
| Gpr3 | 0.195 | 弱 ascr3 偏好 |

## 2. 全谱排名（按 sel_mut 升序）

| # | 突变体 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | 通道 | 强度 | caveat |
|---|--------|------|---------|------------|-----------|------|------|--------|
| 1 | Gpr2_M327A | Gpr2 | -1.391 | -6.744 | -5.353 | A | strong |  |
| 2 | Gpr2_M327D | Gpr2 | -1.089 | -6.666 | -5.577 | A | strong |  |
| 3 | Gpr2_R59F | Gpr2 | -0.956 | -6.658 | -5.702 | A | strong |  |
| 4 | GprC_L377H | GprC | -0.928 | -6.966 | -6.038 | A | strong |  |
| 5 | Gpr2_R59A | Gpr2 | -0.925 | -6.528 | -5.603 | A | strong |  |
| 6 | Gpr3_V138R | Gpr3 | -0.875 | -6.136 | -5.261 | A | strong |  |
| 7 | GprC_L377R | GprC | -0.862 | -6.493 | -5.631 | A | strong |  |
| 8 | GprC_V91C | GprC | -0.857 | -6.874 | -6.017 | A | strong |  |
| 9 | GprC_R174I | GprC | -0.778 | -7.012 | -6.234 | A | strong |  |
| 10 | GprC_L377A | GprC | -0.758 | -6.529 | -5.771 | A | strong | ⚠ GprC-ala |
| 11 | GprC_R174Y | GprC | -0.719 | -6.701 | -5.982 | A | strong |  |
| 12 | GprC_Q411T | GprC | -0.673 | -7.143 | -6.470 | A | strong |  |
| 13 | GprC_Q411R | GprC | -0.658 | -7.072 | -6.414 | A | strong |  |
| 14 | GprC_L377I | GprC | -0.643 | -6.826 | -6.183 | A | strong |  |
| 15 | GprC_V91D | GprC | -0.627 | -6.963 | -6.336 | A | strong |  |
| 16 | Gpr2_M327F | Gpr2 | -0.620 | -5.518 | -4.898 | A | strong |  |
| 17 | GprC_V91P | GprC | -0.620 | -6.848 | -6.228 | A | strong |  |
| 18 | Gpr2_R59E | Gpr2 | -0.616 | -6.401 | -5.785 | A | strong |  |
| 19 | GprC_V91Q | GprC | -0.599 | -6.993 | -6.394 | A | strong |  |
| 20 | Gpr3_I141A | Gpr3 | -0.591 | -5.192 | -4.601 | A | strong |  |
| 21 | GprC_V91M | GprC | -0.591 | -7.028 | -6.437 | A | strong |  |
| 22 | GprC_V91L | GprC | -0.588 | -6.917 | -6.329 | A | strong |  |
| 23 | Gpr2_M327Q | Gpr2 | -0.552 | -6.292 | -5.740 | A | strong |  |
| 24 | Gpr2_R59K | Gpr2 | -0.544 | -6.249 | -5.705 | A | strong |  |
| 25 | Gpr2_R59H | Gpr2 | -0.534 | -6.156 | -5.622 | A | strong |  |
| 26 | GprC_L377T | GprC | -0.516 | -7.461 | -6.945 | A | strong |  |
| 27 | GprC_R174G | GprC | -0.503 | -6.506 | -6.003 | A | strong |  |
| 28 | Gpr3_F170E | Gpr3 | -0.501 | -6.253 | -5.752 | A | strong |  |
| 29 | GprC_L377K | GprC | -0.498 | -6.652 | -6.154 | A | strong |  |
| 30 | GprC_R174V | GprC | -0.492 | -6.740 | -6.248 | A | strong |  |
| 31 | Gpr2_R59C | Gpr2 | -0.484 | -6.036 | -5.552 | A | strong |  |
| 32 | Gpr2_M327R | Gpr2 | -0.483 | -6.454 | -5.971 | A | strong |  |
| 33 | GprC_Q411D | GprC | -0.466 | -6.799 | -6.333 | neutral | moderate |  |
| 34 | GprC_V91E | GprC | -0.462 | -6.836 | -6.374 | neutral | moderate |  |
| 35 | Gpr3_F170D | Gpr3 | -0.443 | -6.213 | -5.770 | neutral | moderate |  |
| 36 | GprC_R174F | GprC | -0.439 | -6.634 | -6.195 | neutral | moderate |  |
| 37 | Gpr2_T124A | Gpr2 | -0.438 | -6.492 | -6.054 | neutral | moderate |  |
| 38 | GprC_R395A | GprC | -0.428 | -6.146 | -5.718 | neutral | moderate | ⚠ GprC-ala |
| 39 | GprC_R174P | GprC | -0.427 | -6.774 | -6.347 | neutral | moderate |  |
| 40 | GprC_L377C | GprC | -0.414 | -6.330 | -5.916 | neutral | moderate |  |
| 41 | GprC_R174A | GprC | -0.406 | -6.629 | -6.223 | neutral | moderate | ⚠ GprC-ala |
| 42 | GprC_Q411N | GprC | -0.406 | -6.742 | -6.336 | neutral | moderate |  |
| 43 | Gpr2_K326A | Gpr2 | -0.404 | -5.960 | -5.556 | neutral | moderate |  |
| 44 | GprC_V91I | GprC | -0.404 | -7.196 | -6.792 | neutral | moderate |  |
| 45 | GprC_N60A | GprC | -0.402 | -6.800 | -6.398 | neutral | moderate | ⚠ GprC-ala |
| 46 | GprC_V91K | GprC | -0.386 | -6.837 | -6.451 | neutral | moderate |  |
| 47 | GprC_V91F | GprC | -0.383 | -6.869 | -6.486 | neutral | moderate |  |
| 48 | GprC_L377F | GprC | -0.375 | -7.334 | -6.959 | neutral | moderate |  |
| 49 | GprC_V91R | GprC | -0.360 | -6.839 | -6.479 | neutral | moderate |  |
| 50 | Gpr2_M327N | Gpr2 | -0.359 | -6.322 | -5.963 | neutral | moderate |  |
| 51 | GprC_V91S | GprC | -0.359 | -6.753 | -6.394 | neutral | moderate |  |
| 52 | GprC_R174C | GprC | -0.337 | -6.604 | -6.267 | neutral | moderate |  |
| 53 | GprC_N378V | GprC | -0.326 | -6.303 | -5.977 | neutral | moderate |  |
| 54 | Gpr2_R59T | Gpr2 | -0.321 | -5.803 | -5.482 | neutral | moderate |  |
| 55 | Gpr2_R59L | Gpr2 | -0.316 | -5.935 | -5.619 | neutral | moderate |  |
| 56 | GprC_Q411W | GprC | -0.316 | -6.700 | -6.384 | neutral | moderate |  |
| 57 | GprC_L377Y | GprC | -0.312 | -6.800 | -6.488 | neutral | moderate |  |
| 58 | GprC_R174S | GprC | -0.310 | -6.541 | -6.231 | neutral | moderate |  |
| 59 | Gpr2_M327P | Gpr2 | -0.304 | -6.121 | -5.817 | neutral | moderate |  |
| 60 | Gpr2_M327V | Gpr2 | -0.300 | -6.201 | -5.901 | neutral | moderate |  |
| 61 | GprC_V91G | GprC | -0.284 | -7.070 | -6.786 | neutral | moderate |  |
| 62 | Gpr2_R59M | Gpr2 | -0.275 | -5.994 | -5.719 | neutral | moderate |  |
| 63 | GprC_R174K | GprC | -0.271 | -6.727 | -6.456 | neutral | moderate |  |
| 64 | Gpr2_R59V | Gpr2 | -0.270 | -5.855 | -5.585 | neutral | moderate |  |
| 65 | Gpr3_V138Y | Gpr3 | -0.267 | -6.345 | -6.078 | neutral | moderate |  |
| 66 | Gpr2_M327Y | Gpr2 | -0.265 | -5.780 | -5.515 | neutral | moderate |  |
| 67 | Gpr3_V138N | Gpr3 | -0.264 | -5.750 | -5.486 | neutral | moderate |  |
| 68 | GprC_L377E | GprC | -0.257 | -6.573 | -6.316 | neutral | moderate |  |
| 69 | GprC_L377V | GprC | -0.257 | -5.976 | -5.719 | neutral | moderate |  |
| 70 | GprC_R174E | GprC | -0.255 | -6.403 | -6.148 | neutral | moderate |  |
| 71 | Gpr3_I141E | Gpr3 | -0.253 | -6.359 | -6.106 | neutral | moderate |  |
| 72 | GprC_N378F | GprC | -0.253 | -6.583 | -6.330 | neutral | moderate |  |
| 73 | Gpr3_V138S | Gpr3 | -0.246 | -5.091 | -4.845 | neutral | moderate |  |
| 74 | Gpr2_R59W | Gpr2 | -0.238 | -6.369 | -6.131 | neutral | moderate |  |
| 75 | GprC_R174Q | GprC | -0.225 | -6.701 | -6.476 | neutral | moderate |  |
| 76 | Gpr3_V138I | Gpr3 | -0.222 | -6.170 | -5.948 | neutral | moderate |  |
| 77 | GprC_Q411M | GprC | -0.222 | -7.185 | -6.963 | neutral | moderate |  |
| 78 | Gpr2_R59D | Gpr2 | -0.211 | -6.057 | -5.846 | neutral | moderate |  |
| 79 | GprC_Q411E | GprC | -0.210 | -6.574 | -6.364 | neutral | moderate |  |
| 80 | GprC_R174D | GprC | -0.200 | -6.398 | -6.198 | neutral | moderate |  |
| 81 | GprC_N378R | GprC | -0.194 | -6.492 | -6.298 | neutral | moderate |  |
| 82 | GprC_Q411G | GprC | -0.193 | -7.157 | -6.964 | neutral | moderate |  |
| 83 | GprC_L377D | GprC | -0.191 | -6.617 | -6.426 | neutral | moderate |  |
| 84 | Gpr3_F170C | Gpr3 | -0.182 | -5.349 | -5.167 | neutral | moderate |  |
| 85 | GprC_N378I | GprC | -0.177 | -6.882 | -6.705 | neutral | moderate |  |
| 86 | Gpr3_I141S | Gpr3 | -0.176 | -6.288 | -6.112 | neutral | moderate |  |
| 87 | Gpr3_F170V | Gpr3 | -0.174 | -5.864 | -5.690 | neutral | moderate |  |
| 88 | GprC_R174L | GprC | -0.174 | -6.430 | -6.256 | neutral | moderate |  |
| 89 | Gpr3_F170A | Gpr3 | -0.164 | -6.042 | -5.878 | neutral | moderate |  |
| 90 | Gpr3_I141P | Gpr3 | -0.164 | -6.318 | -6.154 | neutral | moderate |  |
| 91 | GprC_Q411H | GprC | -0.163 | -7.064 | -6.901 | neutral | moderate |  |
| 92 | Gpr3_V138H | Gpr3 | -0.161 | -6.181 | -6.020 | neutral | moderate |  |
| 93 | GprC_V91Y | GprC | -0.154 | -6.359 | -6.205 | neutral | noise |  |
| 94 | Gpr2_M327S | Gpr2 | -0.150 | -6.289 | -6.139 | neutral | noise |  |
| 95 | Gpr3_F170G | Gpr3 | -0.145 | -5.841 | -5.696 | neutral | noise |  |
| 96 | Gpr2_M327K | Gpr2 | -0.144 | -5.658 | -5.514 | neutral | noise |  |
| 97 | Gpr2_M327I | Gpr2 | -0.137 | -6.072 | -5.935 | neutral | noise |  |
| 98 | GprC_L377M | GprC | -0.132 | -6.646 | -6.514 | neutral | noise |  |
| 99 | GprC_R174T | GprC | -0.127 | -6.098 | -5.971 | neutral | noise |  |
| 100 | GprC_N378W | GprC | -0.125 | -6.977 | -6.852 | neutral | noise |  |
| 101 | Gpr2_Y378A | Gpr2 | -0.119 | -6.073 | -5.954 | neutral | noise |  |
| 102 | Gpr3_I141T | Gpr3 | -0.118 | -6.222 | -6.104 | neutral | noise |  |
| 103 | GprC_V91W | GprC | -0.118 | -7.127 | -7.009 | neutral | noise |  |
| 104 | GprC_L377W | GprC | -0.117 | -6.595 | -6.478 | neutral | noise |  |
| 105 | Gpr3_F170L | Gpr3 | -0.109 | -6.049 | -5.940 | neutral | noise |  |
| 106 | GprC_H189A | GprC | -0.104 | -6.830 | -6.726 | neutral | noise | ⚠ GprC-ala |
| 107 | GprC_N378C | GprC | -0.099 | -6.909 | -6.810 | neutral | noise |  |
| 108 | Gpr2_Y200A | Gpr2 | -0.088 | -6.838 | -6.750 | neutral | noise |  |
| 109 | Gpr2_R59Q | Gpr2 | -0.088 | -5.914 | -5.826 | neutral | noise |  |
| 110 | Gpr3_I141C | Gpr3 | -0.088 | -5.241 | -5.153 | neutral | noise |  |
| 111 | Gpr3_V138K | Gpr3 | -0.080 | -5.399 | -5.319 | neutral | noise |  |
| 112 | GprC_N378H | GprC | -0.077 | -7.219 | -7.142 | neutral | noise |  |
| 113 | Gpr2_M327C | Gpr2 | -0.076 | -6.119 | -6.043 | neutral | noise |  |
| 114 | GprC_V91T | GprC | -0.068 | -7.038 | -6.970 | neutral | noise |  |
| 115 | Gpr3_F170R | Gpr3 | -0.063 | -6.013 | -5.950 | neutral | noise |  |
| 116 | Gpr3_V138A | Gpr3 | -0.061 | -5.753 | -5.692 | neutral | noise |  |
| 117 | Gpr3_F170I | Gpr3 | -0.056 | -5.852 | -5.796 | neutral | noise |  |
| 118 | GprC_V91H | GprC | -0.051 | -6.867 | -6.816 | neutral | noise |  |
| 119 | GprC_Q411F | GprC | -0.049 | -6.567 | -6.518 | neutral | noise |  |
| 120 | Gpr3_I141N | Gpr3 | -0.035 | -5.042 | -5.007 | neutral | noise |  |
| 121 | Gpr3_I141Y | Gpr3 | -0.028 | -5.279 | -5.251 | neutral | noise |  |
| 122 | Gpr3_F170S | Gpr3 | -0.027 | -5.904 | -5.877 | neutral | noise |  |
| 123 | GprC_R174H | GprC | -0.026 | -6.159 | -6.133 | neutral | noise |  |
| 124 | Gpr3_I141R | Gpr3 | -0.023 | -5.169 | -5.146 | neutral | noise |  |
| 125 | Gpr3_F170Y | Gpr3 | -0.014 | -5.955 | -5.941 | neutral | noise |  |
| 126 | Gpr3_I141M | Gpr3 | -0.012 | -5.192 | -5.180 | neutral | noise |  |
| 127 | GprC_R174M | GprC | 0.009 | -6.531 | -6.540 | neutral | noise |  |
| 128 | Gpr2_R59P | Gpr2 | 0.015 | -6.171 | -6.186 | neutral | noise |  |
| 129 | Gpr3_I141H | Gpr3 | 0.017 | -6.090 | -6.107 | neutral | noise |  |
| 130 | Gpr2_M327L | Gpr2 | 0.020 | -5.459 | -5.479 | neutral | noise |  |
| 131 | Gpr3_V138D | Gpr3 | 0.021 | -4.931 | -4.952 | neutral | noise |  |
| 132 | GprC_Q411C | GprC | 0.034 | -6.927 | -6.961 | neutral | noise |  |
| 133 | Gpr2_R59G | Gpr2 | 0.036 | -5.965 | -6.001 | neutral | noise |  |
| 134 | GprC_L377P | GprC | 0.039 | -6.011 | -6.050 | neutral | noise |  |
| 135 | Gpr3_F170W | Gpr3 | 0.040 | -5.949 | -5.989 | neutral | noise |  |
| 136 | GprC_N378P | GprC | 0.043 | -6.407 | -6.450 | neutral | noise |  |
| 137 | Gpr2_R59Y | Gpr2 | 0.052 | -6.145 | -6.197 | neutral | noise |  |
| 138 | Gpr3_D100A | Gpr3 | 0.052 | -6.167 | -6.219 | neutral | noise |  |
| 139 | GprC_L377N | GprC | 0.053 | -6.117 | -6.170 | neutral | noise |  |
| 140 | Gpr3_I178A | Gpr3 | 0.056 | -6.328 | -6.384 | neutral | noise |  |
| 141 | Gpr3_I141G | Gpr3 | 0.077 | -5.989 | -6.066 | neutral | noise |  |
| 142 | Gpr3_N171A | Gpr3 | 0.079 | -6.103 | -6.182 | neutral | noise |  |
| 143 | GprC_L377G | GprC | 0.081 | -6.325 | -6.406 | neutral | noise |  |
| 144 | Gpr3_I141D | Gpr3 | 0.084 | -5.161 | -5.245 | neutral | noise |  |
| 145 | GprC_N378T | GprC | 0.085 | -6.269 | -6.354 | neutral | noise |  |
| 146 | Gpr3_I141Q | Gpr3 | 0.104 | -4.960 | -5.064 | neutral | noise |  |
| 147 | GprC_N378L | GprC | 0.104 | -6.741 | -6.845 | neutral | noise |  |
| 148 | Gpr2_M327T | Gpr2 | 0.107 | -5.991 | -6.098 | neutral | noise |  |
| 149 | Gpr3_F170T | Gpr3 | 0.112 | -5.764 | -5.876 | neutral | noise |  |
| 150 | GprC_V91N | GprC | 0.112 | -7.136 | -7.248 | neutral | noise |  |
| 151 | Gpr3_F170P | Gpr3 | 0.113 | -5.008 | -5.121 | neutral | noise |  |
| 152 | Gpr2_R59S | Gpr2 | 0.116 | -6.204 | -6.320 | neutral | noise |  |
| 153 | GprC_N378D | GprC | 0.118 | -6.897 | -7.015 | neutral | noise |  |
| 154 | GprC_N378Q | GprC | 0.120 | -6.837 | -6.957 | neutral | noise |  |
| 155 | GprC_Q411Y | GprC | 0.120 | -6.942 | -7.062 | neutral | noise |  |
| 156 | GprC_N378E | GprC | 0.129 | -7.250 | -7.379 | neutral | noise |  |
| 157 | GprC_Q411K | GprC | 0.138 | -6.791 | -6.929 | neutral | noise |  |
| 158 | Gpr2_M327W | Gpr2 | 0.142 | -6.634 | -6.776 | neutral | noise |  |
| 159 | Gpr3_I141W | Gpr3 | 0.157 | -6.021 | -6.178 | neutral | noise |  |
| 160 | GprC_Q411V | GprC | 0.159 | -7.113 | -7.272 | neutral | noise |  |
| 161 | Gpr2_M327H | Gpr2 | 0.166 | -4.957 | -5.123 | neutral | moderate |  |
| 162 | Gpr3_V138G | Gpr3 | 0.187 | -5.692 | -5.879 | neutral | moderate |  |
| 163 | GprC_Q411I | GprC | 0.190 | -7.073 | -7.263 | neutral | moderate |  |
| 164 | GprC_Y185A | GprC | 0.192 | -6.383 | -6.575 | neutral | moderate | ⚠ GprC-ala |
| 165 | GprC_R174W | GprC | 0.192 | -6.265 | -6.457 | neutral | moderate |  |
| 166 | Gpr3_I141K | Gpr3 | 0.199 | -4.882 | -5.081 | neutral | moderate |  |
| 167 | Gpr2_M327E | Gpr2 | 0.200 | -4.977 | -5.177 | neutral | moderate |  |
| 168 | GprC_Q415A | GprC | 0.201 | -6.495 | -6.696 | neutral | moderate | ⚠ GprC-ala |
| 169 | Gpr3_I141L | Gpr3 | 0.204 | -4.843 | -5.047 | neutral | moderate |  |
| 170 | GprC_Q411P | GprC | 0.214 | -6.832 | -7.046 | neutral | moderate |  |
| 171 | GprC_N378K | GprC | 0.227 | -7.028 | -7.255 | neutral | moderate |  |
| 172 | GprC_S44A | GprC | 0.234 | -6.278 | -6.512 | neutral | moderate | ⚠ GprC-ala |
| 173 | Gpr3_I141F | Gpr3 | 0.235 | -4.922 | -5.157 | neutral | moderate |  |
| 174 | Gpr2_R59N | Gpr2 | 0.236 | -5.951 | -6.187 | neutral | moderate |  |
| 175 | GprC_N378S | GprC | 0.239 | -7.124 | -7.363 | neutral | moderate |  |
| 176 | Gpr3_V138C | Gpr3 | 0.252 | -5.589 | -5.841 | neutral | moderate |  |
| 177 | Gpr3_V138M | Gpr3 | 0.252 | -5.626 | -5.878 | neutral | moderate |  |
| 178 | Gpr2_N381A | Gpr2 | 0.263 | -5.726 | -5.989 | neutral | moderate |  |
| 179 | GprC_Q411L | GprC | 0.271 | -7.044 | -7.315 | neutral | moderate |  |
| 180 | Gpr2_I120A | Gpr2 | 0.276 | -5.910 | -6.186 | neutral | moderate |  |
| 181 | GprC_L377Q | GprC | 0.277 | -6.269 | -6.546 | neutral | moderate |  |
| 182 | Gpr3_V138W | Gpr3 | 0.284 | -5.617 | -5.901 | neutral | moderate |  |
| 183 | GprC_N378Y | GprC | 0.307 | -6.133 | -6.440 | neutral | moderate |  |
| 184 | Gpr3_V138F | Gpr3 | 0.310 | -4.811 | -5.121 | neutral | moderate |  |
| 185 | Gpr2_I63A | Gpr2 | 0.319 | -6.207 | -6.526 | neutral | moderate |  |
| 186 | GprC_N56A | GprC | 0.341 | -5.579 | -5.920 | neutral | moderate | ⚠ GprC-ala |
| 187 | Gpr3_V138E | Gpr3 | 0.352 | -4.734 | -5.086 | neutral | moderate |  |
| 188 | GprC_N378G | GprC | 0.364 | -6.520 | -6.884 | neutral | moderate |  |
| 189 | Gpr2_Y330A | Gpr2 | 0.367 | -6.060 | -6.427 | neutral | moderate |  |
| 190 | GprC_Y425A | GprC | 0.421 | -6.002 | -6.423 | neutral | moderate | ⚠ GprC-ala |
| 191 | Gpr3_V138Q | Gpr3 | 0.422 | -5.951 | -6.373 | neutral | moderate |  |
| 192 | GprC_P381A | GprC | 0.423 | -6.042 | -6.465 | neutral | moderate | ⚠ GprC-ala |
| 193 | Gpr3_F170M | Gpr3 | 0.454 | -5.286 | -5.740 | neutral | moderate |  |
| 194 | Gpr3_F170Q | Gpr3 | 0.469 | -5.297 | -5.766 | neutral | moderate |  |
| 195 | GprC_N378M | GprC | 0.473 | -6.476 | -6.949 | neutral | moderate |  |
| 196 | Gpr3_F170H | Gpr3 | 0.484 | -5.324 | -5.808 | B | strong |  |
| 197 | GprC_R174N | GprC | 0.485 | -6.135 | -6.620 | B | strong |  |
| 198 | Gpr3_I141V | Gpr3 | 0.490 | -5.501 | -5.991 | B | strong |  |
| 199 | GprC_V91A | GprC | 0.525 | -7.479 | -8.004 | B | strong | ⚠ GprC-ala |
| 200 | Gpr3_Q93A | Gpr3 | 0.580 | -5.531 | -6.111 | B | strong |  |
| 201 | Gpr2_R59I | Gpr2 | 0.594 | -5.362 | -5.956 | B | strong |  |
| 202 | Gpr3_F170N | Gpr3 | 0.616 | -5.219 | -5.835 | B | strong |  |
| 203 | Gpr3_F170K | Gpr3 | 0.632 | -5.310 | -5.942 | B | strong |  |
| 204 | GprC_Q411A | GprC | 0.652 | -5.530 | -6.182 | B | strong | ⚠ GprC-ala |
| 205 | Gpr3_R175A | Gpr3 | 0.663 | -5.302 | -5.965 | B | strong |  |
| 206 | GprC_L377S | GprC | 0.684 | -5.894 | -6.578 | B | strong |  |
| 207 | Gpr3_V138P | Gpr3 | 0.736 | -4.767 | -5.503 | B | strong |  |
| 208 | Gpr2_M327G | Gpr2 | 0.749 | -4.880 | -5.629 | B | strong |  |
| 209 | GprC_Q411S | GprC | 0.759 | -5.333 | -6.092 | B | strong |  |
| 210 | Gpr3_V138L | Gpr3 | 0.886 | -4.818 | -5.704 | B | strong |  |
| 211 | GprC_N378A | GprC | 0.957 | -5.385 | -6.342 | B | strong | ⚠ GprC-ala |
| 212 | Gpr3_V138T | Gpr3 | 1.042 | -5.005 | -6.047 | B | strong |  |

## 3. Channel A 候选（ascr18 偏好，sel_mut < −0.477）

### 3a. 无 caveat

| # | 突变体 | 受体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | ΔΔG(ascr18) |
|---|--------|------|---------|------------|-----------|-------------|
| 1 | Gpr2_M327A | Gpr2 | -1.391 | -6.744 | -5.353 | 0.090 |
| 2 | Gpr2_M327D | Gpr2 | -1.089 | -6.666 | -5.577 | 0.168 |
| 3 | Gpr2_R59F | Gpr2 | -0.956 | -6.658 | -5.702 | 0.176 |
| 4 | GprC_L377H | GprC | -0.928 | -6.966 | -6.038 | 1.309 |
| 5 | Gpr2_R59A | Gpr2 | -0.925 | -6.528 | -5.603 | 0.306 |
| 6 | Gpr3_V138R | Gpr3 | -0.875 | -6.136 | -5.261 | -0.410 |
| 7 | GprC_L377R | GprC | -0.862 | -6.493 | -5.631 | 1.782 |
| 8 | GprC_V91C | GprC | -0.857 | -6.874 | -6.017 | 1.401 |
| 9 | GprC_R174I | GprC | -0.778 | -7.012 | -6.234 | 1.263 |
| 10 | GprC_R174Y | GprC | -0.719 | -6.701 | -5.982 | 1.574 |
| 11 | GprC_Q411T | GprC | -0.673 | -7.143 | -6.470 | 1.132 |
| 12 | GprC_Q411R | GprC | -0.658 | -7.072 | -6.414 | 1.203 |
| 13 | GprC_L377I | GprC | -0.643 | -6.826 | -6.183 | 1.449 |
| 14 | GprC_V91D | GprC | -0.627 | -6.963 | -6.336 | 1.312 |
| 15 | Gpr2_M327F | Gpr2 | -0.620 | -5.518 | -4.898 | 1.316 |
| 16 | GprC_V91P | GprC | -0.620 | -6.848 | -6.228 | 1.427 |
| 17 | Gpr2_R59E | Gpr2 | -0.616 | -6.401 | -5.785 | 0.433 |
| 18 | GprC_V91Q | GprC | -0.599 | -6.993 | -6.394 | 1.282 |
| 19 | Gpr3_I141A | Gpr3 | -0.591 | -5.192 | -4.601 | 0.534 |
| 20 | GprC_V91M | GprC | -0.591 | -7.028 | -6.437 | 1.247 |
| 21 | GprC_V91L | GprC | -0.588 | -6.917 | -6.329 | 1.358 |
| 22 | Gpr2_M327Q | Gpr2 | -0.552 | -6.292 | -5.740 | 0.542 |
| 23 | Gpr2_R59K | Gpr2 | -0.544 | -6.249 | -5.705 | 0.585 |
| 24 | Gpr2_R59H | Gpr2 | -0.534 | -6.156 | -5.622 | 0.678 |
| 25 | GprC_L377T | GprC | -0.516 | -7.461 | -6.945 | 0.814 |
| 26 | GprC_R174G | GprC | -0.503 | -6.506 | -6.003 | 1.769 |
| 27 | Gpr3_F170E | Gpr3 | -0.501 | -6.253 | -5.752 | -0.527 |
| 28 | GprC_L377K | GprC | -0.498 | -6.652 | -6.154 | 1.623 |
| 29 | GprC_R174V | GprC | -0.492 | -6.740 | -6.248 | 1.535 |
| 30 | Gpr2_R59C | Gpr2 | -0.484 | -6.036 | -5.552 | 0.798 |
| 31 | Gpr2_M327R | Gpr2 | -0.483 | -6.454 | -5.971 | 0.380 |

### 3b. GprC alanine scan（⚠ caveat）

| # | 突变体 | sel_mut | ΔG(ascr18) | ΔG(ascr3) | ΔΔG(ascr18) | ΔΔG(ascr3) |
|---|--------|---------|------------|-----------|-------------|-------------|
| 1 | GprC_L377A | -0.758 | -6.529 | -5.771 | 1.746 | 1.706 |

## 4. Channel B 候选（ascr3 偏好，sel_mut > +0.477）

### 4a. 无 caveat

| # | 突变体 | 受体 | sel_mut | ΔG(ascr3) | ΔG(ascr18) | ΔΔG(ascr3) |
|---|--------|------|---------|-----------|------------|-------------|
| 1 | Gpr3_F170H | Gpr3 | 0.484 | -5.808 | -5.324 | 0.113 |
| 2 | GprC_R174N | GprC | 0.485 | -6.620 | -6.135 | 0.857 |
| 3 | Gpr3_I141V | Gpr3 | 0.490 | -5.991 | -5.501 | -0.070 |
| 4 | Gpr3_Q93A | Gpr3 | 0.580 | -6.111 | -5.531 | -0.190 |
| 5 | Gpr2_R59I | Gpr2 | 0.594 | -5.956 | -5.362 | 0.474 |
| 6 | Gpr3_F170N | Gpr3 | 0.616 | -5.835 | -5.219 | 0.086 |
| 7 | Gpr3_F170K | Gpr3 | 0.632 | -5.942 | -5.310 | -0.021 |
| 8 | Gpr3_R175A | Gpr3 | 0.663 | -5.965 | -5.302 | -0.044 |
| 9 | GprC_L377S | GprC | 0.684 | -6.578 | -5.894 | 0.899 |
| 10 | Gpr3_V138P | Gpr3 | 0.736 | -5.503 | -4.767 | 0.418 |
| 11 | Gpr2_M327G | Gpr2 | 0.749 | -5.629 | -4.880 | 0.801 |
| 12 | GprC_Q411S | GprC | 0.759 | -6.092 | -5.333 | 1.385 |
| 13 | Gpr3_V138L | Gpr3 | 0.886 | -5.704 | -4.818 | 0.217 |
| 14 | Gpr3_V138T | Gpr3 | 1.042 | -6.047 | -5.005 | -0.126 |

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
| 1 | Gpr2_M327A | Gpr3_V138T | -2.433 | 0.572 | -1.391 | 1.042 | -6.744 | -6.047 |
| 2 | Gpr2_M327A | Gpr3_V138L | -2.277 | 0.611 | -1.391 | 0.886 | -6.744 | -5.704 |
| 3 | Gpr2_M327A | GprC_Q411S | -2.150 | 0.647 | -1.391 | 0.759 | -6.744 | -6.092 |
| 4 | Gpr2_M327D | Gpr3_V138T | -2.131 | 0.511 | -1.089 | 1.042 | -6.666 | -6.047 |
| 5 | Gpr2_M327A | Gpr3_V138P | -2.127 | 0.654 | -1.391 | 0.736 | -6.744 | -5.503 |
| 6 | Gpr2_M327A | GprC_L377S | -2.075 | 0.670 | -1.391 | 0.684 | -6.744 | -6.578 |
| 7 | Gpr2_M327A | Gpr3_R175A | -2.054 | 0.677 | -1.391 | 0.663 | -6.744 | -5.965 |
| 8 | Gpr2_M327A | Gpr3_F170K | -2.023 | 0.688 | -1.391 | 0.632 | -6.744 | -5.942 |
| 9 | Gpr2_M327A | Gpr3_F170N | -2.007 | 0.693 | -1.391 | 0.616 | -6.744 | -5.835 |
| 10 | Gpr2_R59F | Gpr3_V138T | -1.998 | 0.478 | -0.956 | 1.042 | -6.658 | -6.047 |

### 5b. 含 GprC-ala caveat 配对 Top 10（仅供参考，不直接进入湿实验推荐）

| # | Channel A | Channel B | D | balance | sel_A | sel_B | caveat |
|---|-----------|-----------|---|---------|-------|-------|--------|
| 1 | Gpr2_M327A | GprC_N378A | -2.348 | 0.592 | -1.391 | 0.957 | ⚠ GprC-ala |
| 2 | Gpr2_M327D | GprC_N378A | -2.046 | 0.532 | -1.089 | 0.957 | ⚠ GprC-ala |
| 3 | Gpr2_M327A | GprC_Q411A | -2.043 | 0.681 | -1.391 | 0.652 | ⚠ GprC-ala |
| 4 | Gpr2_M327A | GprC_V91A | -1.916 | 0.726 | -1.391 | 0.525 | ⚠ GprC-ala |
| 5 | Gpr2_R59F | GprC_N378A | -1.913 | 0.500 | -0.956 | 0.957 | ⚠ GprC-ala |
| 6 | Gpr2_R59A | GprC_N378A | -1.882 | 0.491 | -0.925 | 0.957 | ⚠ GprC-ala |
| 7 | Gpr3_V138R | GprC_N378A | -1.832 | 0.478 | -0.875 | 0.957 | ⚠ GprC-ala |
| 8 | Gpr2_M327D | GprC_Q411A | -1.741 | 0.626 | -1.089 | 0.652 | ⚠ GprC-ala |
| 9 | Gpr2_M327D | GprC_V91A | -1.614 | 0.675 | -1.089 | 0.525 | ⚠ GprC-ala |
| 10 | Gpr2_R59F | GprC_Q411A | -1.608 | 0.595 | -0.956 | 0.652 | ⚠ GprC-ala |

## 6. 湿实验配对建议

基于无 caveat 跨受体配对 Top 3：

1. **Gpr2_M327A** (Channel A, sel=-1.391) + **Gpr3_V138T** (Channel B, sel=1.042)
   - D = -2.433, balance = 0.572
   - 亲和力：A端 ΔG(ascr18) = -6.744, B端 ΔG(ascr3) = -6.047

2. **Gpr2_M327A** (Channel A, sel=-1.391) + **Gpr3_V138L** (Channel B, sel=0.886)
   - D = -2.277, balance = 0.611
   - 亲和力：A端 ΔG(ascr18) = -6.744, B端 ΔG(ascr3) = -5.704

3. **Gpr2_M327A** (Channel A, sel=-1.391) + **GprC_Q411S** (Channel B, sel=0.759)
   - D = -2.150, balance = 0.647
   - 亲和力：A端 ΔG(ascr18) = -6.744, B端 ΔG(ascr3) = -6.092

## 7. 边界与 caveat

1. **GprC alanine scan caveat**：GprC 13/14 个 Ala 突变体显示非特异性结合破坏（ΔΔG(ascr18) 常 >2 kcal/mol），产生的表观 ascr3 偏好是差异化破坏副产品，不代表真正的选择性工程。这些候选须经 saturation scan 验证后才可进入湿实验。
2. **噪声阈值**：基于 Gpr2_ascr18 multiseed SD=0.159，这是系统中最大的 SD，作为保守估计。|sel_mut| < 0.477 的选择性差异不可靠。
3. **刚性对接局限**：AutoDock Vina 刚性对接不考虑蛋白柔性和溶剂效应，ΔG 绝对值仅作相对排名参考，不代表真实结合自由能。
4. **亲和力下限**：Channel 候选要求 |ΔG| ≥ 5.0 kcal/mol，确保突变体仍有足够结合力激活信号通路。参照系统最弱 WT = Gpr3_ascr18 = −5.726。

## 附录：统计摘要

| 类别 | 数量 |
|------|------|
| 总突变数 | 212 |
| Channel A 无 caveat | 31 |
| Channel A 含 GprC-ala caveat | 1 |
| Channel B 无 caveat | 14 |
| Channel B 含 GprC-ala caveat | 3 |
| 中性区 | 163 |
| 跨受体配对 (无 caveat) | 334 |
| 跨受体配对 (含 caveat) | 42 |
