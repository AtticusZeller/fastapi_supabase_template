# # Additional assertions based on your application's logic
# import pytest
# from app.schemas import Token
# from faker import Faker
# from starlette.testclient import TestClient

# from supabase._async.client import AsyncClient
# from tests.utils import get_auth_header


# @pytest.mark.anyio
# async def test_create_item(client: TestClient, token: Token) -> None:

#     headers = get_auth_header(token.access_token)

#     test_data = Faker().sentence()


#     response = client.post(
#         "/api/v1/items/create-item", headers=headers, json={"test_data": test_data}
#     )
#     assert response.status_code == 200
#     assert response.json()["test_data"] == test_data


# @pytest.mark.anyio
# async def test_read_all_items(client: TestClient, token: Token) -> None:
#     headers = get_auth_header(token.access_token)

#     response = client.get("/api/v1/items/read-all-item", headers=headers)
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)


# @pytest.mark.anyio
# async def test_read_item_by_id(client: TestClient, token: Token) -> None:
#     headers = get_auth_header(token.access_token)
#     test_data = Faker().sentence()


#     create_response = client.post(
#         "/api/v1/items/create-item", headers=headers, json={"test_data": test_data}
#     )
#     assert create_response.status_code == 200
#     created_item_id = create_response.json()["id"]


#     read_response = client.get(
#         f"/api/v1/items/get-by-id/{created_item_id}", headers=headers
#     )
#     assert read_response.status_code == 200
#     assert read_response.json()["id"] == created_item_id
#     assert read_response.json()["test_data"] == test_data


# @pytest.mark.anyio
# async def test_read_item_by_owner(
#     client: TestClient, token: Token, db: AsyncClient
# ) -> None:
#     headers = get_auth_header(token.access_token)
#     test_data = Faker().sentence()

#     client.post(
#         "/api/v1/items/create-item", headers=headers, json={"test_data": test_data}
#     )

#     user = await db.auth.get_user(jwt=token.access_token)
#     user_id = user.user.id

#     read_response = client.get("/api/v1/items/get-by-owner", headers=headers)
#     assert read_response.status_code == 200
#     items = read_response.json()
#     assert isinstance(items, list)
#     assert all(item["user_id"] == user_id for item in items)


# @pytest.mark.anyio
# async def test_update_item(client: TestClient, token: Token) -> None:
#     headers = get_auth_header(token.access_token)
#     test_data = Faker().sentence()
#     create_response = client.post(
#         "/api/v1/items/create-item", headers=headers, json={"test_data": test_data}
#     )
#     assert create_response.status_code == 200
#     created_item = create_response.json()
#     created_item_id = created_item["id"]
#     updated_data = {"test_data": Faker().sentence(), "id": created_item_id}

#     update_response = client.put(
#         "/api/v1/items/update-item", headers=headers, json=updated_data
#     )
#     assert update_response.status_code == 200
#     assert update_response.json()["test_data"] == updated_data["test_data"]


# @pytest.mark.anyio
# async def test_delete_item(client: TestClient, token: Token) -> None:
#     headers = get_auth_header(token.access_token)
#     test_data = Faker().sentence()
#     create_response = client.post(
#         "/api/v1/items/create-item", headers=headers, json={"test_data": test_data}
#     )
#     assert create_response.status_code == 200
#     created_item_id = create_response.json()["id"]

#     delete_response = client.delete(
#         f"/api/v1/items/delete/{created_item_id}", headers=headers
#     )
#     assert delete_response.status_code == 200

#     get_response = client.get(
#         f"/api/v1/items/get-by-id/{created_item_id}", headers=headers
#     )
#     assert get_response.status_code == 200
#     assert get_response.json() is None
