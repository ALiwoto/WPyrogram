/*
 * Pyrogram - Telegram MTProto API Client Library for Python
 * Copyright (C) 2017-present Dan <https://github.com/delivrance>
 *
 * This file is part of Pyrogram.
 *
 * Pyrogram is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Pyrogram is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Derived from TgCrypto 1.2.5; maintained as WPyrogram's private extension. */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "aes256.h"
#include "ige256.h"
#include "ctr256.h"
#include "cbc256.h"

static PyObject *block_cipher(PyObject *args, uint8_t encrypt, uint8_t use_ige) {
    Py_buffer data, key, iv;
    PyObject *result = NULL;
    uint8_t *output = NULL;
    uint8_t key_copy[32], iv_copy[32];
    Py_ssize_t iv_size = use_ige ? 32 : 16;

    if (!PyArg_ParseTuple(args, "y*y*y*", &data, &key, &iv)) {
        return NULL;
    }
    if (data.len == 0 || data.len % AES_BLOCK_SIZE != 0) {
        PyErr_SetString(PyExc_ValueError, "Data must be a nonempty multiple of 16 bytes");
        goto cleanup;
    }
    if (key.len != 32) {
        PyErr_SetString(PyExc_ValueError, "Key size must be exactly 32 bytes");
        goto cleanup;
    }
    if (iv.len != iv_size) {
        PyErr_Format(PyExc_ValueError, "IV size must be exactly %zd bytes", iv_size);
        goto cleanup;
    }

    memcpy(key_copy, key.buf, sizeof(key_copy));
    memcpy(iv_copy, iv.buf, (size_t) iv_size);
    Py_BEGIN_ALLOW_THREADS
    if (use_ige) {
        output = ige256(data.buf, (size_t) data.len, key_copy, iv_copy, encrypt);
    } else {
        output = cbc256(data.buf, (size_t) data.len, key_copy, iv_copy, encrypt);
    }
    Py_END_ALLOW_THREADS

    if (output == NULL) {
        PyErr_NoMemory();
    } else {
        result = PyBytes_FromStringAndSize((const char *) output, data.len);
    }

cleanup:
    free(output);
    PyBuffer_Release(&data);
    PyBuffer_Release(&key);
    PyBuffer_Release(&iv);
    return result;
}

static PyObject *ige256_encrypt(PyObject *self, PyObject *args) {
    return block_cipher(args, 1, 1);
}

static PyObject *ige256_decrypt(PyObject *self, PyObject *args) {
    return block_cipher(args, 0, 1);
}

static PyObject *cbc256_encrypt(PyObject *self, PyObject *args) {
    return block_cipher(args, 1, 0);
}

static PyObject *cbc256_decrypt(PyObject *self, PyObject *args) {
    return block_cipher(args, 0, 0);
}

static PyObject *ctr256_crypt(PyObject *self, PyObject *args) {
    Py_buffer data, key, iv, state;
    PyObject *result = NULL;
    uint8_t *output = NULL;
    uint8_t key_copy[32], iv_copy[16], state_copy;

    if (!PyArg_ParseTuple(args, "y*y*w*w*", &data, &key, &iv, &state)) {
        return NULL;
    }
    if (data.len == 0) {
        PyErr_SetString(PyExc_ValueError, "Data must not be empty");
        goto cleanup;
    }
    if (key.len != 32) {
        PyErr_SetString(PyExc_ValueError, "Key size must be exactly 32 bytes");
        goto cleanup;
    }
    if (iv.len != 16) {
        PyErr_SetString(PyExc_ValueError, "IV size must be exactly 16 bytes");
        goto cleanup;
    }
    if (state.len != 1 || *(uint8_t *) state.buf > 15) {
        PyErr_SetString(PyExc_ValueError, "State must be one writable byte in the range [0, 15]");
        goto cleanup;
    }

    memcpy(key_copy, key.buf, sizeof(key_copy));
    memcpy(iv_copy, iv.buf, sizeof(iv_copy));
    state_copy = *(uint8_t *) state.buf;
    Py_BEGIN_ALLOW_THREADS
    output = ctr256(data.buf, (size_t) data.len, key_copy, iv_copy, &state_copy);
    Py_END_ALLOW_THREADS

    if (output == NULL) {
        PyErr_NoMemory();
    } else {
        result = PyBytes_FromStringAndSize((const char *) output, data.len);
        if (result != NULL) {
            memcpy(iv.buf, iv_copy, sizeof(iv_copy));
            *(uint8_t *) state.buf = state_copy;
        }
    }

cleanup:
    free(output);
    PyBuffer_Release(&data);
    PyBuffer_Release(&key);
    PyBuffer_Release(&iv);
    PyBuffer_Release(&state);
    return result;
}

static PyMethodDef methods[] = {
    {"ige256_encrypt", ige256_encrypt, METH_VARARGS, "AES-256-IGE encryption."},
    {"ige256_decrypt", ige256_decrypt, METH_VARARGS, "AES-256-IGE decryption."},
    {"ctr256_encrypt", ctr256_crypt, METH_VARARGS, "AES-256-CTR encryption; updates writable IV and state."},
    {"ctr256_decrypt", ctr256_crypt, METH_VARARGS, "AES-256-CTR decryption; updates writable IV and state."},
    {"cbc256_encrypt", cbc256_encrypt, METH_VARARGS, "AES-256-CBC encryption."},
    {"cbc256_decrypt", cbc256_decrypt, METH_VARARGS, "AES-256-CBC decryption."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_tgcrypto",
    "WPyrogram's bundled TgCrypto AES implementation.",
    -1,
    methods
};

PyMODINIT_FUNC PyInit__tgcrypto(void) {
    return PyModule_Create(&module);
}
