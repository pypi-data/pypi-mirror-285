import matplotlib.pyplot as plt

# 데이터 정의
data = {
    "curve_uls": [
        {"stress": 0, "strain": 0},
        {"stress": 0, "strain": 0.0004500000000000001},
        {"stress": 10.2, "strain": 0.0004500000000000001},
        {"stress": 10.2, "strain": 0.003}
    ],
    "curve_sls": [
        {"stress": 0, "strain": 0},
        {"stress": 12, "strain": 0.003}
    ]
}

# curve_uls 데이터 추출
uls_stress = [point["stress"] for point in data["curve_uls"]]
uls_strain = [point["strain"] for point in data["curve_uls"]]

# curve_sls 데이터 추출
sls_stress = [point["stress"] for point in data["curve_sls"]]
sls_strain = [point["strain"] for point in data["curve_sls"]]

# 그래프 그리기
plt.plot(uls_strain, uls_stress, marker='o', label='Curve ULS')
plt.plot(sls_strain, sls_stress, marker='o', label='Curve SLS')

# 축 레이블 추가
plt.xlabel('Strain')
plt.ylabel('Stress')

# 그래프 제목 추가
plt.title('MaterialConcrete Stress-Strain Graph (C12, ACI318M-19)')

# 범례 추가
plt.legend()

# 그래프 표시
plt.grid(True)
plt.show()