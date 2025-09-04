<?php
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['register'])) {
    include 'auth.php';
    $username = $_POST['username'];
    $password = $_POST['password'];
    if (register($username, $password)) {
        echo "<p style='color: green;'>Registration successful! <a href='login.html'>Login here</a></p>";
    } else {
        echo "<p style='color: red;'>Username already exists</p>";
        echo "<p><a href='register.html'>Try again</a></p>";
    }
}
?>