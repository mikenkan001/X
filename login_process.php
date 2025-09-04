<?php
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['login'])) {
    include 'auth.php';
    $username = $_POST['username'];
    $password = $_POST['password'];
    if (login($username, $password)) {
        header("Location: index.html");
        exit;
    } else {
        echo "<p style='color: red;'>Invalid username or password</p>";
        echo "<p><a href='login.html'>Try again</a></p>";
    }
}
?>