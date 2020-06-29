from numpy import *

# ��ĳһ��������ֵ
def lwlr(testPoint, xArr, yArr, k = 1.0):
    xMat = mat(xArr); yMat = mat(yArr).T
    m = shape(xMat)[0]
    weights = mat(eye((m)))
    for i in range(m):
        diffMat = testPoint - xMat[i, :]
        weights[i, i] = exp(diffMat * diffMat.T/(-2.0 * k**2))      # ����Ȩ�ضԽǾ���
    xTx = xMat.T * (weights * xMat)                                 # ��������ܼ���
    if linalg.det(xTx) == 0.0:
        print('This Matrix is singular, cannot do inverse')
        return
    theta = xTx.I * (xMat.T * (weights * yMat))                     # ����ع�ϵ��
    return testPoint * theta

# �����е�������ֵ
def lwlrTest(testArr, xArr, yArr, k = 1.0):
    m = shape(testArr)[0]
    yHat = zeros(m)
    for i in range(m):
        yHat[i] = lwlr(testArr[i], xArr, yArr, k)
    return yHat