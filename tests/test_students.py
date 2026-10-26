def student(**updates):
    data = {"name": "Asha Sharma", "date_of_birth": "2005-04-12",
            "email": "asha@example.com", "phone": "9800000000",
            "course": "Computer Science", "address": "Birgunj, Nepal",
            "enrollment_date": "2025-08-01"}
    data.update(updates)
    return data

def test_crud_lifecycle(client):
    response = client.post("/students", json=student())
    assert response.status_code == 201
    sid = response.json()["id"]
    assert client.get("/students").json()["total"] == 1
    assert client.get(f"/students/{sid}").status_code == 200
    patched = client.patch(f"/students/{sid}", json={"course": "AI & ML"})
    assert patched.status_code == 200 and patched.json()["course"] == "AI & ML"
    replaced = client.put(f"/students/{sid}", json=student(name="Asha Updated", email="updated@example.com"))
    assert replaced.status_code == 200 and replaced.json()["name"] == "Asha Updated"
    assert client.delete(f"/students/{sid}").status_code == 204
    assert client.get(f"/students/{sid}").status_code == 404

def test_duplicate_email(client):
    assert client.post("/students", json=student()).status_code == 201
    assert client.post("/students", json=student(name="Other")).status_code == 409

def test_invalid_email(client):
    assert client.post("/students", json=student(email="bad-email")).status_code == 422

def test_future_birth_date(client):
    assert client.post("/students", json=student(date_of_birth="2999-01-01")).status_code == 422

def test_contact_required(client):
    assert client.post("/students", json=student(email=None, phone=None)).status_code == 422

def test_missing_student(client):
    assert client.get("/students/99999").status_code == 404
    assert client.delete("/students/99999").status_code == 404

def test_filter_stats_and_export(client):
    client.post("/students", json=student())
    client.post("/students", json=student(name="Ravi Kumar", email="ravi@example.com", course="Data Science"))
    assert client.get("/students?course=Data").json()["total"] == 1
    assert client.get("/stats").json()["total_students"] == 2
    export = client.get("/students/export.csv")
    assert export.status_code == 200 and "Asha Sharma" in export.text

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_student_pagination(client):
    # Create three students.
    students = [
        student(name="Asha Sharma", email="asha@example.com"),
        student(name="Ravi Kumar", email="ravi@example.com"),
        student(name="Mina Thapa", email="mina@example.com"),
    ]

    for data in students:
        response = client.post("/students", json=data)
        assert response.status_code == 201

    # Request only two students.
    first_page = client.get("/students?limit=2&offset=0")
    assert first_page.status_code == 200
    assert first_page.json()["total"] == 3
    assert len(first_page.json()["items"]) == 2

    # Request the next page.
    second_page = client.get("/students?limit=2&offset=2")
    assert second_page.status_code == 200
    assert len(second_page.json()["items"]) == 1


def test_student_pagination_validation(client):
    assert client.get("/students?limit=0").status_code == 422
    assert client.get("/students?limit=101").status_code == 422
    assert client.get("/students?offset=-1").status_code == 422


def test_student_filter_with_pagination(client):
    client.post("/students", json=student())
    client.post(
        "/students",
        json=student(
            name="Ravi Kumar",
            email="ravi@example.com",
            course="Data Science",
        ),
    )
    client.post(
        "/students",
        json=student(
            name="Mina Thapa",
            email="mina@example.com",
            course="Computer Science",
        ),
    )

    response = client.get(
        "/students?course=Computer&limit=1&offset=0"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 1
    assert data["offset"] == 0
    assert len(data["items"]) == 1
    assert data["items"][0]["course"] == "Computer Science"
