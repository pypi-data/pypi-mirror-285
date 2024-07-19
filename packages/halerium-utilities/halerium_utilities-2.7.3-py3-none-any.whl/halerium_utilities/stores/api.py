import os
from typing import List, Union

import httpx

from halerium_utilities.stores.chunker import Document

tenant = os.getenv('HALERIUM_TENANT_KEY')
workspace = os.getenv('HALERIUM_PROJECT_ID')
runnerId = os.getenv('HALERIUM_ID')
runnerToken = os.getenv('HALERIUM_TOKEN')
baseUrl = os.getenv('HALERIUM_BASE_URL')


API_TIMEOUT = 120


class InformationStoreException(Exception):

    def __init__(self, msg):
        super().__init__(msg)


def get_workspace_information_stores():
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def get_workspace_information_stores_async():
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def get_information_store_info(store_id):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def get_information_store_info_async(store_id):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def add_information_store(name):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"name": name}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def add_information_store_async(name):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"name": name}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def rename_information_store(store_id, new_name):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"name": new_name}

    with httpx.Client() as client:
        response = client.put(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def rename_information_store_async(store_id, new_name):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"name": new_name}

    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def delete_information_store(store_id):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    with httpx.Client() as client:
        response = client.delete(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def delete_information_store_async(store_id):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def add_memory_to_store(store_id, memory: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}/memories"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"memory": memory}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def add_memory_to_store_async(store_id, memory: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/stores/{store_id}/memories"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"memory": memory}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def add_file_to_vectorstore(vectorstore_id, filepath: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/files"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"filepath": filepath}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def add_file_to_vectorstore_async(vectorstore_id, filepath: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/files"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"filepath": filepath}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def add_chunks_to_vectorstore(vectorstore_id, chunks: List[Union[Document, dict]]):
    """
    Every item in the chunks list must look like this
    {"content": "...", "metadata": {...}}
    """
    chunks = [Document.validate(c) for c in chunks]

    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = [chunk.dict() for chunk in chunks]

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not add chunks to vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def add_chunks_to_vectorstore_async(vectorstore_id, chunks: List[Union[Document, dict]]):
    """
    Every item in the chunks list must look like this
    {"content": "...", "metadata": {...}}
    """
    chunks = [Document.validate(c) for c in chunks]

    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = [chunk.dict() for chunk in chunks]

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def query_vectorstore(vectorstore_id, query, max_results=5, post_filter=None):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/vector-store/"

    data = {
        "query": query,
        "max_results": max_results,
        "post_filter": post_filter,
        "threshold": .7,
        "document_id": vectorstore_id,
        "tenant": tenant,
        "workspace": workspace,
    }

    headers = {
        "halerium-runner-token": runnerToken,
    }

    with httpx.Client() as client:
        response = client.get(url, params=data, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def query_vectorstore_async(vectorstore_id, query, max_results=5, post_filter=None):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/vector-store/"

    data = {
        "query": query,
        "max_results": max_results,
        "post_filter": post_filter,
        "threshold": .7,
        "document_id": vectorstore_id,
        "tenant": tenant,
        "workspace": workspace,
    }

    headers = {
        "halerium-runner-token": runnerToken,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=data, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def get_file_as_text(filepath: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/files"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"filepath": filepath}

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def get_file_as_text_async(filepath: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/files"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"filepath": filepath}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("could not set vectorstore (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def get_chunks(vectorstore_id: str, start=0, size=1000):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"start": start, "size": size}

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def get_chunks_async(vectorstore_id: str, start=0, size=1000):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = {"start": start, "size": size}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def get_chunk(vectorstore_id: str, chunk_id: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/{chunk_id}"
    headers = {
        "halerium-runner-token": runnerToken,
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def get_chunk_async(vectorstore_id: str, chunk_id: str):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/{chunk_id}"
    headers = {
        "halerium-runner-token": runnerToken,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def edit_chunk(vectorstore_id: str, chunk_id: str, document: Union[Document, dict]):
    document = Document.validate(document)

    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/{chunk_id}"
    headers = {
        "halerium-runner-token": runnerToken,
    }

    with httpx.Client() as client:
        response = client.put(url, headers=headers, json=document.dict(), timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def edit_chunk_async(vectorstore_id: str, chunk_id: str, document: Union[Document, dict]):
    document = Document.validate(document)

    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/{chunk_id}"
    headers = {
        "halerium-runner-token": runnerToken,
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=document.dict(), timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


def delete_chunks(vectorstore_id: str, chunk_ids: list[str]):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = chunk_ids

    with httpx.Client() as client:
        response = client.delete(url, headers=headers, json=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()


async def delete_chunks_async(vectorstore_id: str, chunk_ids: list[str]):
    url = f"{baseUrl}/api/tenants/{tenant}/projects/{workspace}/runners/{runnerId}/information-store/vectorstore/{vectorstore_id}/chunks/"

    headers = {
        "halerium-runner-token": runnerToken,
    }

    payload = chunk_ids

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers, json=payload, timeout=API_TIMEOUT)

    if response.status_code != 200:
        raise InformationStoreException("Error (%d)...\n%s" % (response.status_code, response.text))

    return response.json()
