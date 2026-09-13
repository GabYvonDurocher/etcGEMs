"""D42 numerical likelihood geometry from archived pilot centres."""
import hashlib
import argparse
import json
import signal
import time
import numpy as np
from scipy.optimize import minimize
import controls as c

HERE=c.HERE/'independence_laplace'
ACTIVE=np.array([i for i in range(15) if i!=7])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--central',action='store_true');args=parser.parse_args()
    HERE.mkdir(exist_ok=True)
    source=c.HERE/'independence_controls/spike_pilot.json'
    pilot=json.loads(source.read_text())['mixture']; target=c.Target('spike')
    means=[];covariances=[];records=[];start=time.monotonic()
    def expired(*unused):raise TimeoutError('D42 geometry fit60s cap')
    signal.signal(signal.SIGALRM,expired);signal.alarm(60)
    for centre,cov in zip(pilot['means'],pilot['covariances']):
        origin=np.array(centre)[ACTIVE];scale=np.sqrt(np.diag(cov))[ACTIVE];calls=0
        def objective(z):
            nonlocal calls
            calls+=1
            if calls>20000:raise RuntimeError('D42 fit call cap')
            u=np.full(15,.5);u[ACTIVE]=origin+scale*z
            return -target(u)
        bounds=list(zip(-origin/scale,(1-origin)/scale))
        def gradient(z):
            basis=np.eye(14)*1e-4
            return np.array([(objective(z+b)-objective(z-b))/(2e-4) for b in basis])
        result=minimize(objective,np.zeros(14),method='L-BFGS-B',bounds=bounds,jac=gradient if args.central else None,
                        options={'eps':1e-4,'maxiter':500,'maxfun':19000,'ftol':1e-12,'gtol':1e-6})
        if not result.success:
            (HERE/('central_failure.json' if args.central else 'forward_failure.json')).write_text(json.dumps(dict(message=str(result.message),calls=calls,x=result.x.tolist(),fun=float(result.fun),jac=result.jac.tolist(),component=len(records)),indent=2))
            raise RuntimeError(str(result.message))
        mean=np.full(15,.5);mean[ACTIVE]=origin+scale*result.x
        if np.any((mean[ACTIVE]<=0)|(mean[ACTIVE]>=1)):raise RuntimeError('D42 bound optimum')
        def hessian(step):
            x=result.x;v=objective(x);h=np.empty((14,14));basis=np.eye(14)*step
            for i in range(14):
                h[i,i]=(objective(x+basis[i])-2*v+objective(x-basis[i]))/step**2
                for j in range(i):
                    h[i,j]=h[j,i]=(objective(x+basis[i]+basis[j])-objective(x+basis[i]-basis[j])-objective(x-basis[i]+basis[j])+objective(x-basis[i]-basis[j]))/(4*step**2)
            return h
        h=hessian(.001);h2=hessian(.002);error=np.linalg.norm(h-h2)/np.linalg.norm(h2)
        if error>=1e-3:raise RuntimeError('D42 unstable curvature')
        np.linalg.cholesky(h)
        covariance=np.zeros((15,15));covariance[np.ix_(ACTIVE,ACTIVE)]=np.linalg.inv(h)*np.outer(scale,scale);covariance[7,7]=1/12
        np.linalg.cholesky(covariance)
        means.append(mean.tolist());covariances.append(covariance.tolist())
        records.append(dict(optimisation_message=str(result.message),iterations=int(result.nit),calls=calls,
                            curvature_relative_difference=float(error),scaled_hessian=h.tolist(),mean=mean.tolist()))
    signal.alarm(0)
    output=dict(mixture=dict(means=means,covariances=covariances,uniform_weight=.1),records=records,
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),wall_s=time.monotonic()-start)
    with (HERE/'fitted_proposal.json').open('x') as out:json.dump(output,out,indent=2)
    print(json.dumps(dict(wall_s=output['wall_s'],calls=[r['calls'] for r in records],
                         curvature_errors=[r['curvature_relative_difference'] for r in records])))

if __name__=='__main__':main()
