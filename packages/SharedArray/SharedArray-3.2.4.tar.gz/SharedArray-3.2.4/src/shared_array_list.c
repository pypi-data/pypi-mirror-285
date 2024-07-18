/*
 * This file is part of SharedArray.
 * Copyright (C) 2014-2018 Mathieu Mirmont <mat@parad0x.org>
 *
 * SharedArray is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * SharedArray is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SharedArray.  If not, see <http://www.gnu.org/licenses/>.
 */

/* This only works on Linux where SHM segments are implemented as
 * regular files in a tmpfs filesystem. There doesn't seem to be a
 * portable way of listing SHM segments. */
#ifdef __linux__

#define NPY_NO_DEPRECATED_API	NPY_1_8_API_VERSION
#define PY_ARRAY_UNIQUE_SYMBOL	SHARED_ARRAY_ARRAY_API
#define NO_IMPORT_ARRAY

#include <Python.h>
#include <structseq.h>
#include <numpy/arrayobject.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dirent.h>
#include <unistd.h>
#include <string.h>
#include "shared_array.h"

/* SHM directory */
#define SHMDIR	"/dev/shm"

/*
 * List of meta-data
 */
struct list {
	struct list *next;
	PyObject *desc;
};

/*
 * Read the meta data from a shared memory area
 */
static int get_meta(const char *filename, struct array_meta *meta)
{
	struct stat file_info;
	char path[PATH_MAX];
	int fd;
	int ret = -1;

	/* Construct the file name */
	snprintf(path, sizeof (path), "%s/%s", SHMDIR, filename);

	/* Open the file */
	if ((fd = open(path, O_RDONLY)) < 0)
		goto ret;

	/* Find its size */
	if (fstat(fd, &file_info) < 0)
		goto ret;

	/* Ignore short files */
	if (file_info.st_size < (off_t) sizeof (*meta))
		goto ret;

	/* Seek to the meta data location */
	if (lseek(fd, file_info.st_size - sizeof (*meta), SEEK_SET) < 0)
		goto ret;

	/* Read the meta data structure */
	if (read(fd, meta, sizeof (*meta)) != sizeof (*meta))
		goto ret;

	/* Success */
	ret = 0;

ret:	/* Cleanup before returning */
	if (fd > 0)
		close(fd);
	return ret;
}

/*
 * Convert the dims array into a tuple
 */
static PyObject *convert_dims(int ndims, npy_intp *dims)
{
	PyObject *tuple = PyTuple_New(ndims);
	int i;

	for (i = 0; i < ndims; i++)
		PyTuple_SET_ITEM(tuple, i, PyLong_FromLong(dims[i]));
	return tuple;
}

/*
 * Add an element to the list
 */
static struct list *list_extend(struct list *next, struct array_meta *meta, const char *name)
{
	struct list *list;
	npy_intp dims[NPY_MAXDIMS];

	/* Copy the dims[] array out of the packed structure */
	for (int i = 0; i < meta->ndims; i++)
		dims[i] = meta->dims[i];

	/* Allocate the new list element */
	if (!(list = malloc(sizeof (*list)))) {
		PyErr_NoMemory();
		return next;
	}

	/* Populate the list */
	list->next = next;
	list->desc = PyStructSequence_New(&PyArrayDescObject_Type);

	PyStructSequence_SET_ITEM(list->desc, 0, PyBytes_FromString(name));
	PyStructSequence_SET_ITEM(list->desc, 1, PyArray_TypeObjectFromType(meta->typenum));
	PyStructSequence_SET_ITEM(list->desc, 2, convert_dims(meta->ndims, dims));

	/* Return the new element */
	return list;
}

/*
 * List all arrays created in shared memory
 */
static int build_list(struct list **list)
{
	struct dirent *entry;
	int size = 0;
	DIR *dir;

	/* Start the list */
	*list = NULL;

	/* Open the directory */
	if (!(dir = opendir(SHMDIR))) {
		PyErr_SetFromErrnoWithFilename(PyExc_OSError, SHMDIR);
		return -1;
	}

	/* Process each directory entry */
	while ((entry = readdir(dir))) {
		struct array_meta meta;

		/* Only accept regular files */
		if (entry->d_type != DT_REG)
			continue;

		/* Get our meta-data structure out of it */
		if (get_meta(entry->d_name, &meta) < 0)
			continue;

		/* Ignore things that aren't shared arrays */
		if (strncmp(meta.magic, SHARED_ARRAY_MAGIC, sizeof (meta.magic)))
			continue;

		/* Add valid entries to the list */
		*list = list_extend(*list, &meta, entry->d_name);
		size++;
	}

	/* Close the directory */
	closedir(dir);

	/* Return the size */
	return size;
}

/*
 * Free the list
 */
static void free_list(struct list *list)
{
	while (list) {
		struct list *next = list->next;

		free(list);
		list = next;
	}
}

/*
 * Build a tuple from the list
 */
static PyObject *build_tuple(struct list *list, int size)
{
	PyObject *tuple = PyTuple_New(size);
	int i;

	for (i = 0; i < size; i++) {
		PyTuple_SetItem(tuple, i, list->desc);
		list = list->next;
	}
	return tuple;
}

/*
 * Method: SharedArray.list()
 */
PyObject *shared_array_list(PyObject *self, PyObject *args)
{
	PyObject *tuple;
	struct list *list;
	int size;

	/* Parse the arguments */
	if (!PyArg_ParseTuple(args, ""))
		return NULL;

	/* Build the list of shared arrays */
	if ((size = build_list(&list)) < 0)
		return NULL;

	/* Convert the list into a tuple */
	tuple = build_tuple(list, size);

	/* Free the list */
	free_list(list);

	/* Return the tuple */
	return tuple;
}

#endif /* __linux__ */
