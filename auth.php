<?php
session_start();

function initDatabase() {
    $db = new SQLite3('database.db');
    $db->exec('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL)');
    return $db;
}

function register($username, $password) {
    $db = initDatabase();
    $stmt = $db->prepare('SELECT username FROM users WHERE username = :username');
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $result = $stmt->execute();
    if ($result->fetchArray()) {
        $db->close();
        return false; // Username exists
    }
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $db->prepare('INSERT INTO users (username, password) VALUES (:username, :password)');
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $stmt->bindValue(':password', $hashedPassword, SQLITE3_TEXT);
    $result = $stmt->execute();
    $db->close();
    return true;
}

function login($username, $password) {
    $db = initDatabase();
    $stmt = $db->prepare('SELECT password FROM users WHERE username = :username');
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $result = $stmt->execute();
    $row = $result->fetchArray(SQLITE3_ASSOC);
    $db->close();
    if ($row && password_verify($password, $row['password'])) {
        $_SESSION['user'] = $username;
        return true;
    }
    return false;
}
?>