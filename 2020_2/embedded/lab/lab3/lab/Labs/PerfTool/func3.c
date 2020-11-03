#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>		//close()
#include <malloc.h>
#include <fcntl.h>

#define min(a, b) ((a) < (b) ? (a) : (b))

void initialize_matrices(int N, int B, int *x_origin, int *y, int *z) {
	int i, j;
	for(i=0;i<N;i++) {
		for(j=0;j<N;j++) {
			x_origin[i*N+j] = 0;
			y[i*N+j] = 2;
			z[i*N+j] = 3;
		}
	}
}

void multiply_matrices_optimized(int N, int B, int *x_blocking, int *y, int *z) {
	int jj, kk, i, j, k, r;
	for(jj=0;jj<N;jj=jj+B) {
		for(kk=0;kk<N;kk=kk+B) {
			for(i=0;i<N;i++){
				for(j=jj;j<min(jj+B,N);j++) {
					r=0;
					for(k=kk;k<min(kk+B,N);k++) {
						r+=y[i*N+k]*z[k*N+j];
					}
					x_blocking[i*N+j]+=r;
				}
			}
		}
	}
}

int check_result(int *x_origin, int *x_blocking, int N) {
	int i, j, diff_count = 0;

	for(i=0;i<N;i++) {
		for(j=0;j<N;j++) {
			if(x_origin[i*N+j] != x_blocking[i*N+j]) diff_count++;
		}
	}

	if(diff_count) 
		return 0;
	else 
		return 1;
}

int main(int argc, char **argv) {
	int *x_blocking, *y, *z;
	int N, B;
	
	N = 300;
    B = 30;

	/***** The result for blocking code *****/
	x_blocking = (int *)malloc(N*N*sizeof(int));
	/****************************************/
	
	y = (int *)malloc(N*N*sizeof(int));
	z = (int *)malloc(N*N*sizeof(int));

	//-------------------------------
	// Blocking code
	//-------------------------------
	initialize_matrices(N, B, x_blocking, y, z);

	multiply_matrices_optimized(N, B, x_blocking, y, z);


	free(x_blocking);
	free(y);
	free(z);
	
	return 0;
}
