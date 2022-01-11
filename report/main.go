package main
 
import (
    "database/sql"
    "os"
    "fmt"
    "github.com/go-sql-driver/mysql"
)

func getEnv(key, fallback string) string {
    value, exists := os.LookupEnv(key)
    if !exists {
        value = fallback
    }
    return value
}

func main() {
 
    cfg := mysql.Config{
        User:   os.Getenv("MYSQL_USER"),
        Passwd: os.Getenv("MYSQL_PASS"),
        Net:    "tcp",
        Addr:   getEnv("MYSQL_HOST", "localhost") + ":" + getEnv("MYSQL_PORT", "3306"),
        DBName: os.Getenv("MYSQL_DATABASE"),
    }    

    db, err := sql.Open("mysql", cfg.FormatDSN())
    if err != nil {
        panic(err)
    }
     
    err = db.Ping()
    if err != nil {
        panic(err)
    }
     
    fmt.Print("Pong")     
    defer db.Close()
}