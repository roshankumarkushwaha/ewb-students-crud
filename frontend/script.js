
const API_BASE_URL = "https://ewb-students-crud-hbhd.onrender.com";

const studentForm = document.getElementById("studentForm");
const studentTableBody = document.getElementById("studentTableBody");
const totalStudents = document.getElementById("totalStudents");
const formMessage = document.getElementById("formMessage");
const listMessage = document.getElementById("listMessage");
const submitButton = document.getElementById("submitButton");
const refreshButton = document.getElementById("refreshButton");

function showMessage(element, message, type = "") {
    element.textContent = message;
    element.className = type;
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
            Accept: "application/json",
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...options.headers
        }
    });

    if (!response.ok) {
        let message = `Request failed (${response.status})`;

        try {
            const error = await response.json();
            message = error.detail
                ? (typeof error.detail === "string"
                    ? error.detail
                    : JSON.stringify(error.detail))
                : message;
        } catch {
            // Keep the HTTP status message if the response isn't JSON.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

async function loadStudents() {
    studentTableBody.replaceChildren();

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");
    loadingCell.colSpan = 6;
    loadingCell.className = "empty-cell";
    loadingCell.textContent = "Loading students...";
    loadingRow.appendChild(loadingCell);
    studentTableBody.appendChild(loadingRow);

    showMessage(listMessage, "");

    try {
        const data = await apiRequest("/students?limit=100&offset=0");

        totalStudents.textContent = data.total;

        studentTableBody.replaceChildren();

        if (!data.items || data.items.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 6;
            cell.className = "empty-cell";
            cell.textContent = "No students found. Add your first student above.";
            row.appendChild(cell);
            studentTableBody.appendChild(row);
            return;
        }

        data.items.forEach(student => {
            const row = document.createElement("tr");

            const values = [
                student.id,
                student.name,
                student.email,
                student.course || "—",
                student.phone || "—"
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = String(value);
                row.appendChild(cell);
            });

            const actionsCell = document.createElement("td");

            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.textContent = "Edit";
            editButton.className = "secondary-button";
            editButton.addEventListener("click", () => editStudent(student));

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.textContent = "Delete";
            deleteButton.style.marginLeft = "6px";
            deleteButton.addEventListener("click", () => deleteStudent(student));

            actionsCell.append(editButton, deleteButton);
            row.appendChild(actionsCell);

            studentTableBody.appendChild(row);
        });
    } catch (error) {
        totalStudents.textContent = "—";

        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 6;
        cell.className = "empty-cell";
        cell.textContent = "Could not load students. Check your connection and try Refresh.";
        row.appendChild(cell);
        studentTableBody.replaceChildren(row);

        showMessage(listMessage, error.message, "message-error");
    }
}

studentForm.addEventListener("submit", async event => {
    event.preventDefault();

    showMessage(formMessage, "");

    const formData = new FormData(studentForm);
    const student = Object.fromEntries(formData.entries());

    // Empty optional values are sent as null.
    ["phone", "course", "address", "enrollment_date"].forEach(key => {
        if (!student[key]) {
            student[key] = null;
        }
    });

    submitButton.disabled = true;
    submitButton.textContent = "Saving...";

    try {
        await apiRequest("/students", {
            method: "POST",
            body: JSON.stringify(student)
        });

        showMessage(formMessage, "Student added successfully!", "message-success");
        studentForm.reset();
        await loadStudents();
    } catch (error) {
        showMessage(formMessage, `Could not add student: ${error.message}`, "message-error");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Add Student";
    }
});

function editStudent(student) {
    const newCourse = prompt(
        `Enter the new course for ${student.name}:`,
        student.course || ""
    );

    if (newCourse === null) {
        return;
    }

    updateStudentCourse(student, newCourse.trim());
}

async function updateStudentCourse(student, course) {
    try {
        await apiRequest(`/students/${student.id}`, {
            method: "PATCH",
            body: JSON.stringify({ course })
        });

        showMessage(listMessage, "Student updated successfully.", "message-success");
        await loadStudents();
    } catch (error) {
        showMessage(listMessage, `Could not update student: ${error.message}`, "message-error");
    }
}

async function deleteStudent(student) {
    const confirmed = confirm(
        `Delete student "${student.name}" (ID ${student.id})? This cannot be undone.`
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(`/students/${student.id}`, {
            method: "DELETE"
        });

        showMessage(listMessage, "Student deleted successfully.", "message-success");
        await loadStudents();
    } catch (error) {
        showMessage(listMessage, `Could not delete student: ${error.message}`, "message-error");
    }
}

refreshButton.addEventListener("click", loadStudents);

// Load records when the page opens.
loadStudents();
