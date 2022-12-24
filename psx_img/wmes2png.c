#include "png.h"

const int BPP = 4;
const int WIDTH = 288;
const int HEIGHT = 48;
const int BYTE_PER_ROW = WIDTH/8 * BPP;

#define ERROR -1
#define OK 0

int main(int argc, const char** argv) {
	if (argc != 3) {
		printf("usage: wmes2png in out.png\n");
		return (ERROR);
	}

	// try to acquire input and output file handles
	FILE *img;
	img = fopen(argv[1],"rb");
	if(img == NULL){
		printf("could not open input file\n");
		return (ERROR);
	}
	FILE *out = fopen(argv[2], "wb");
	if (!out) {
		printf("could not open output file\n");
		return (ERROR);
	}

	// allocate png_struct and png_info
	png_structp png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
	if (!png_ptr)
		return (ERROR);

	png_infop info_ptr = png_create_info_struct(png_ptr);
	if (!info_ptr) {
		png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
		return (ERROR);
	}
	// error handler (default) (?) (?)
	if (setjmp(png_jmpbuf(png_ptr))) {
		png_destroy_write_struct(&png_ptr, &info_ptr);
		fclose(out);
		return (ERROR);
	}

	png_init_io(png_ptr, out);

	// read img data and set up row pointers
	png_byte data[HEIGHT][BYTE_PER_ROW];
	fread(data, HEIGHT*BYTE_PER_ROW, 1, img);
	png_bytep row_pointers[HEIGHT];
	for (int i=0; i<HEIGHT; i++){
		row_pointers[i] = (png_bytep)data[i];
	}
	fclose(img);
	png_set_rows(png_ptr, info_ptr, (png_bytepp)&row_pointers);

	// png info
	png_set_IHDR(png_ptr, info_ptr, WIDTH, HEIGHT, BPP, PNG_COLOR_TYPE_PALETTE,
	             PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);

	png_color palette[16];
	palette[0] = (png_color){0, 0, 0};
	palette[1] = (png_color){82, 41, 132};
	palette[9] = (png_color){255, 255, 255};
	png_set_PLTE(png_ptr, info_ptr, palette, 16);

	// index 0 is transparent color
	png_set_tRNS(png_ptr, info_ptr, &(png_byte){0}, 1, NULL);

	// write file header info
	png_write_info(png_ptr, info_ptr);

	// img has nybble order reversed from expected, use packswap
	png_set_packswap(png_ptr);

	// write the image data and IEND
	png_write_image(png_ptr, row_pointers);
	png_write_end(png_ptr, info_ptr);

	// clean up
	png_destroy_write_struct(&png_ptr, &info_ptr);
	fclose(out);
	return (OK);
}
