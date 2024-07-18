#define PY_SSIZE_T_CLEAN
#include <Python.h>

char HEX[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
unsigned char HEXV [256] = {
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  0, 0, 0, 0, 0, 0, 0, 10, 11, 12, 13, 14, 15, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 10, 11, 12, 13, 14, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};


static const int  c_reprb_fsm_start  = 0;
static const int  c_reprb_fsm_first_final  = 0;
static const int  c_reprb_fsm_error  = -1;
static const int  c_reprb_fsm_en_main  = 0;
PyObject* c_reprb(PyObject* self, PyObject* args) {
	PyObject* bytes_obj;
	if (!PyArg_ParseTuple(args, "O", &bytes_obj)) {
		return NULL;
	}
	if (!PyBytes_Check(bytes_obj)) {
		PyErr_SetString(PyExc_TypeError, "Expected a bytes object");
		return NULL;
	}
	
	unsigned char* input_bytes = (unsigned char*)PyBytes_AS_STRING(bytes_obj);
	Py_ssize_t input_length = PyBytes_GET_SIZE(bytes_obj);
	
	unsigned char* buf = (unsigned char*)malloc(input_length * 4);  
	if (buf == NULL) {
		return NULL;
	}
	unsigned char* res = buf;
	int cs;
	unsigned char * p = input_bytes;
	unsigned char * pe = input_bytes + input_length;
	
	{
		cs = ( int ) c_reprb_fsm_start;
		
	}
	{
		switch ( cs  ) {
			case 0:
			goto st_case_0;
			
		}
		_ctr1:
		{
			*buf++ =  '\\'; 
			*buf++ =  'x'; 
			*buf++ = HEX[(((*( p  ))
			)) >> 4];
			*buf++ = HEX[(((*( p  ))
			)) & 0xF];
			
		}
		
		
		goto _st0;
		_ctr2:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  '0'; 
		}
		
		
		goto _st0;
		_ctr3:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  'a'; 
		}
		
		
		goto _st0;
		_ctr4:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  'b'; 
		}
		
		
		goto _st0;
		_ctr5:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  't'; 
		}
		
		
		goto _st0;
		_ctr6:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  'n'; 
		}
		
		
		goto _st0;
		_ctr7:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  'f'; 
		}
		
		
		goto _st0;
		_ctr8:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  'r'; 
		}
		
		
		goto _st0;
		_ctr9:
		{
			*buf++ =  (((*( p  ))
			));
		}
		
		
		goto _st0;
		_ctr10:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  '"'; 
		}
		
		
		goto _st0;
		_ctr11:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  '\'';
		}
		
		
		goto _st0;
		_ctr12:
		{
			*buf++ =  '\\'; 
		}
		{
			*buf++ =  '\\';
		}
		
		
		goto _st0;
		_st0:
		p+= 1;
		st_case_0:
		if ( p == pe  )
		goto _out0;
		
		switch ( ((*( p  ))
		) ) {
			case 0:
			{
				goto _ctr2;
				
			}
			case 7:
			{
				goto _ctr3;
				
			}
			case 8:
			{
				goto _ctr4;
				
			}
			case 9:
			{
				goto _ctr5;
				
			}
			case 10:
			{
				goto _ctr6;
				
			}
			case 12:
			{
				goto _ctr7;
				
			}
			case 13:
			{
				goto _ctr8;
				
			}
			case 34:
			{
				goto _ctr10;
				
			}
			case 39:
			{
				goto _ctr11;
				
			}
			case 92:
			{
				goto _ctr12;
				
			}
			
		}
		if ( 32 <= ((*( p  ))
		)&& ((*( p  ))
		)<= 126  )
		{
			goto _ctr9;
			
		}
		
		goto _ctr1;
		_out0: cs = 0;
		goto _out; 
		_out: {
		
		}
		
	}
	size_t res_length = buf - res;
	// trans to python bytes object
	PyObject* py_bytes = Py_BuildValue("y#", res, res_length);
	
	// release 
	free(res);  
	
	return py_bytes;
}

static const int  c_evals_fsm_start  = 2;
static const int  c_evals_fsm_first_final  = 2;
static const int  c_evals_fsm_error  = -1;
static const int  c_evals_fsm_en_main  = 2;
PyObject* c_evalb(PyObject* self, PyObject* args) {
	PyObject* bytes_obj;
	if (!PyArg_ParseTuple(args, "O", &bytes_obj)) {
		return NULL;
	}
	if (!PyBytes_Check(bytes_obj)) {
		PyErr_SetString(PyExc_TypeError, "Expected a bytes object");
		return NULL;
	}
	
	unsigned char* input_bytes = (unsigned char*)PyBytes_AS_STRING(bytes_obj);
	Py_ssize_t input_length = PyBytes_GET_SIZE(bytes_obj);
	unsigned char* buf = (unsigned char*)malloc(input_length);  
	if (buf == NULL) {
		return NULL;
	}
	
	unsigned char* res = buf;
	int cs;
	unsigned char *  ts;
	unsigned char *  te;
	int cp_len;
	unsigned char value = 0;
	unsigned char * p = input_bytes;
	unsigned char * pe = input_bytes + input_length;
	unsigned char * eof = pe;
	
	{
		cs = ( int ) c_evals_fsm_start;
		ts = 0;
		te = 0;
		
	}
	{
		switch ( cs  ) {
			case 2:
			goto st_case_2;
			case 3:
			goto st_case_3;
			case 4:
			goto st_case_4;
			case 0:
			goto st_case_0;
			case 1:
			goto st_case_1;
			
		}
		_ctr0:
		{
			{
				p = ((te))-1;
				{
					*buf++ = (((*( p  ))
					));
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr2:
		{
			value = (value<<4) + HEXV[(((*( p  ))
			))];
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr6:
		{
			{
				te = p;
				p = p - 1;
				{
					cp_len = p + 1 - ts; memcpy(buf, ts, cp_len); buf+= cp_len;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr7:
		{
			{
				te = p;
				p = p - 1;
				{
					*buf++ = (((*( p  ))
					));
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr8:
		{
			value = '"' ;
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr9:
		{
			value = '\'';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr10:
		{
			value = 0   ;
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr11:
		{
			value = '\\';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr12:
		{
			value = '\a';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr13:
		{
			value = '\b';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr14:
		{
			value = '\f';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr15:
		{
			value = '\n';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr16:
		{
			value = '\r';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr17:
		{
			value = '\t';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_ctr18:
		{
			value = '\v';
		}
		{
			{
				te = p+1;
				{
					*buf++ = value;
				}
				
			}
			
		}
		
		
		goto _st2;
		_st2:
		if ( p == eof  )
		goto _out2;
		
		{
			{
				ts = 0;
				
			}
			
		}
		
		
		p+= 1;
		st_case_2:
		if ( p == pe && p != eof  )
		goto _out2;
		
		{
			{
				ts = p;
				
			}
			
		}
		if ( p == eof  )
		{
			goto _st2;
		}
		
		else
		{
			if ( ((*( p  ))
			)== 92  )
			{
				goto _ctr5;
				
			}
			
			goto _st3;
			
		}
		
		_st3:
		if ( p == eof  )
		goto _out3;
		
		p+= 1;
		st_case_3:
		if ( p == pe && p != eof  )
		goto _out3;
		
		if ( p == eof  )
		{
			goto _ctr6;
		}
		
		else
		{
			if ( ((*( p  ))
			)== 92  )
			{
				goto _ctr6;
				
			}
			
			goto _st3;
			
		}
		
		_ctr5:
		{
			{
				te = p+1;
				
			}
			
		}
		
		
		goto _st4;
		_st4:
		if ( p == eof  )
		goto _out4;
		
		p+= 1;
		st_case_4:
		if ( p == pe && p != eof  )
		goto _out4;
		
		if ( p == eof  )
		{
			goto _ctr7;
		}
		
		else
		{
			switch ( ((*( p  ))
			) ) {
				case 34:
				{
					goto _ctr8;
					
				}
				case 39:
				{
					goto _ctr9;
					
				}
				case 48:
				{
					goto _ctr10;
					
				}
				case 92:
				{
					goto _ctr11;
					
				}
				case 97:
				{
					goto _ctr12;
					
				}
				case 98:
				{
					goto _ctr13;
					
				}
				case 102:
				{
					goto _ctr14;
					
				}
				case 110:
				{
					goto _ctr15;
					
				}
				case 114:
				{
					goto _ctr16;
					
				}
				case 116:
				{
					goto _ctr17;
					
				}
				case 118:
				{
					goto _ctr18;
					
				}
				case 120:
				{
					goto _ctr19;
					
				}
				
			}
			goto _ctr7;
			
		}
		
		_ctr19:
		{
			value = 0   ;
		}
		
		
		goto _st0;
		_st0:
		if ( p == eof  )
		goto _out0;
		
		p+= 1;
		st_case_0:
		if ( p == pe && p != eof  )
		goto _out0;
		
		if ( p == eof  )
		{
			goto _ctr0;
		}
		
		else
		{
			if ( ((*( p  ))
			)< 65  )
			{
				if ( 48 <= ((*( p  ))
				)&& ((*( p  ))
				)<= 57  )
				{
					goto _ctr1;
					
				}
				
				
			}
			
			else if ( ((*( p  ))
			)> 70  )
			{
				if ( 97 <= ((*( p  ))
				)&& ((*( p  ))
				)<= 102  )
				{
					goto _ctr1;
					
				}
				
				
			}
			
			else
			{
				goto _ctr1;
				
			}
			
			goto _ctr0;
			
		}
		
		_ctr1:
		{
			value = (value<<4) + HEXV[(((*( p  ))
			))];
		}
		
		
		goto _st1;
		_st1:
		if ( p == eof  )
		goto _out1;
		
		p+= 1;
		st_case_1:
		if ( p == pe && p != eof  )
		goto _out1;
		
		if ( p == eof  )
		{
			goto _ctr0;
		}
		
		else
		{
			if ( ((*( p  ))
			)< 65  )
			{
				if ( 48 <= ((*( p  ))
				)&& ((*( p  ))
				)<= 57  )
				{
					goto _ctr2;
					
				}
				
				
			}
			
			else if ( ((*( p  ))
			)> 70  )
			{
				if ( 97 <= ((*( p  ))
				)&& ((*( p  ))
				)<= 102  )
				{
					goto _ctr2;
					
				}
				
				
			}
			
			else
			{
				goto _ctr2;
				
			}
			
			goto _ctr0;
			
		}
		
		_out2: cs = 2;
		goto _out; 
		_out3: cs = 3;
		goto _out; 
		_out4: cs = 4;
		goto _out; 
		_out0: cs = 0;
		goto _out; 
		_out1: cs = 1;
		goto _out; 
		_out: {
		
		}
		
	}
	size_t res_length = buf - res;
	// trans to python bytes object
	PyObject* py_bytes = Py_BuildValue("y#", res, res_length);
	
	// release 
	free(res);  
	
	return py_bytes;
}

static PyMethodDef Methods[] = {
	{"c_reprb", c_reprb, METH_VARARGS, "repr bytes"},
	{"c_evalb", c_evalb, METH_VARARGS, "eval bytes"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
	PyModuleDef_HEAD_INIT,
	"_reprb",
	NULL,
	-1,
	Methods
};

PyMODINIT_FUNC PyInit__reprb(void) {
	return PyModule_Create(&module);
}