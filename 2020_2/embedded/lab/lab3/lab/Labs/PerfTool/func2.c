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

void multiply_matrices(int N, int B, int *x_origin, int *y, int *z) {
	int r, i ,j, k;
	for(i=0;i<N;i++){
		for(j=0;j<N;j++){
			r=0;
			for(k=0;k<N;k++){
				r+=y[i*N+k]*z[k*N+j];
			}
			x_origin[i*N+j]=r;
		}
	}
}

int main(int argc, char **argv) {
	int *x_origin, *y, *z;
	int N, B;
	
	N = 300;
  	B = 30;

	/***** The result for original code *****/
	x_origin = (int *)malloc(N*N*sizeof(int));
	/****************************************/

	y = (int *)malloc(N*N*sizeof(int));
	z = (int *)malloc(N*N*sizeof(int));

	//-------------------------------
	// Original code
	//-------------------------------
	// Initialization
	initialize_matrices(N, B, x_origin, y, z);

	multiply_matrices(N, B, x_origin, y, z);



	free(x_origin);
	free(y);
	free(z);
	
	return 0;
}
