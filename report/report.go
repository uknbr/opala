package main

import (
    "database/sql"
    "fmt"
    "log"

    _ "github.com/go-sql-driver/mysql"
)

var db *sql.DB

func main() {
    // Capture connection properties.
    cfg := mysql.Config{
        User:   os.Getenv("DBUSER"),
        Passwd: os.Getenv("DBPASS"),
        Net:    "tcp",
        Addr:   "127.0.0.1:3306",
        DBName: "recordings",
    }
    // Get a database handle.
    var err error
    db, err = sql.Open("mysql", cfg.FormatDSN())
    if err != nil {
        log.Fatal(err)
    }

    pingErr := db.Ping()
    if pingErr != nil {
        log.Fatal(pingErr)
    }
    fmt.Println("Connected!")
}

func main() {

    db, err := sql.Open("mysql", "user7:s$cret@tcp(127.0.0.1:3306)/testdb")
    defer db.Close()

    if err != nil {
        log.Fatal(err)
    }

    var version string

    err2 := db.QueryRow("SELECT VERSION()").Scan(&version)

    if err2 != nil {
        log.Fatal(err2)
    }

    fmt.Println(version)
}
