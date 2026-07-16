const GUEST_LOGIN = {
  email: "guest@kanmind.de",
  password: "asdasdasd",
};

const IS_LOCALHOST = ["127.0.0.1", "localhost"].includes(window.location.hostname);

const API_BASE_URL = IS_LOCALHOST ? "http://127.0.0.1:8000/api/" : "/api/";

const LOGIN_URL = "login/";

const REGISTER_URL = "registration/";

const BOARDS_URL = "boards/";

const MAIL_CHECK_URL = "email-check/";

const TASKS_URL = "tasks/";

const TASKS_ASSIGNED_URL = "tasks/assigned-to-me/";

const TASKS_REVIEWER_URL = "tasks/reviewing/";
