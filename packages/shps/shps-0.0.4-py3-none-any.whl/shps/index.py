
nu = 0.3
E = 100.

ijkl = {
    k: v for k,v in zip(range(9),
            [(1,1) , (2,2) , (3,3) , (1,2) , (2,1) , (2,3) , (3,2) , (3,1) , (1,3)])
}

import numpy as np

m = np.array([1, 1, 1, 0, 0, 0])[:,None]
print(m@m.T)

Pvol = 1/3*m@m.T
Pdev = np.eye(6) - 1/3*m@m.T
e = np.array([5, 0, 0, 0, 0, 0])
print(Pdev@e)
print(Pvol@e)

s = E/(1+nu)*(e + nu/(1-2*nu)*sum(e[:3])*m[:,0])
Cdev = E/(1+nu)*Pdev

print(s)
print(Pdev@s)
print(Cdev@e)
print(Cdev@Pdev@e)
print(Pdev)


