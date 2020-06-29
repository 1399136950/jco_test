from numpy import *

# 对某一点计算估计值
def lwlr(testPoint, xArr, yArr, k = 1.0):
    xMat = mat(xArr); yMat = mat(yArr).T
    m = shape(xMat)[0]
    weights = mat(eye((m)))
    for i in range(m):
        diffMat = testPoint - xMat[i, :]
        weights[i, i] = exp(diffMat * diffMat.T/(-2.0 * k**2))      # 计算权重对角矩阵
    xTx = xMat.T * (weights * xMat)                                 # 奇异矩阵不能计算
    if linalg.det(xTx) == 0.0:
        print('This Matrix is singular, cannot do inverse')
        return
    theta = xTx.I * (xMat.T * (weights * yMat))                     # 计算回归系数
    return testPoint * theta

# 对所有点计算估计值
def lwlrTest(testArr, xArr, yArr, k = 1.0):
    m = shape(testArr)[0]
    yHat = zeros(m)
    for i in range(m):
        yHat[i] = lwlr(testArr[i], xArr, yArr, k)
    return yHat