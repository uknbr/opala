package main
 
import (
    "database/sql"
    "os"
    "fmt"
    "github.com/go-sql-driver/mysql"
    //telegram "github.com/go-telegram-bot-api/telegram-bot-api/v5"
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
    fmt.Print("Connected to DB\n")

    err = db.Ping()
    if err != nil {
        panic(err)
    }
    fmt.Print("Got success server response!\n")

    // Total executions
    var status_count string
    err = db.QueryRow("select count(1) from status").Scan(&status_count)
    if err != nil {
        panic(err.Error())
    }

    // Offer count
    var offer_count string
    err = db.QueryRow("select count(1) from offer").Scan(&offer_count)
    if err != nil {
        panic(err.Error())
    }

    // Average price
    var price_avg string
    err = db.QueryRow("select format(avg(price),2) from offer where price > 1000 and price < 1000000").Scan(&price_avg)
    if err != nil {
        panic(err.Error())
    }

    // Average score
    var score_avg string
    err = db.QueryRow("select format(avg(score),2) from score").Scan(&score_avg)
    if err != nil {
        panic(err.Error())
    }

    // Recommendation
    var offer_best string
    err = db.QueryRow("select code from score order by score desc limit 1").Scan(&offer_best)
    if err != nil {
        panic(err.Error())
    }

    // Show
    fmt.Print("\nNro de pesquisas: " + status_count + "\nNro de anuncios: " + offer_count + "\nMedia de preço: R$ " + price_avg + "\nMedia de pontos: " + score_avg + "\nAnucio destaque: https://www.olx.com.br/vi/" + offer_best)
    defer db.Close()

    //bot, err := telegram.NewBotAPI("MyAwesomeBotToken")
	//if err != nil {
	//	log.Panic(err)
	//}
    //
    //fmt.Print("Authorized on account %s", bot.Self.UserName)
    //telegram.NewMessage(telegram_chat, telegram_msg)
}