package main

import (
	"os"
	"fmt"
	"strings"
	"time"
	"github.com/gocolly/colly"
	"github.com/jmoiron/sqlx"
	"github.com/robfig/cron"
	_ "github.com/go-sql-driver/mysql"
)

const (
	URL = "http://finance.eastmoney.com/yaowen.html"
)

func main() {
	fmt.Println("Task start\n---------------------------------------------")
	sche := cron.New()
	host := GetHost()
	sche.AddFunc("@hourly", func(){
		news := visit(URL)
		db := DB{"fund", "123456", host, 3306, "fund_filter", nil}
		db.Connect()
		db.InsertAll(news)
		defer db.Close()
		info := fmt.Sprintf("%v visited eastmoney", time.Now().Format("2006-01-01 15:04:05"))
		fmt.Println(info)
	})
	sche.Start()
	select{}
}

type EastMoney struct{
	Title string
	Abstract string
	Url string
	Datetime string
	Source string
}
/*
 * 爬虫部分
*/ 
func visit(url string) []EastMoney{
	var news []EastMoney
	c := colly.NewCollector()

	c.OnError(func(_ *colly.Response, err error) {
		fmt.Println("Something went wrong:", err)
	})

	c.OnHTML("div[id=artitileList1]", func(e *colly.HTMLElement) {
		e.ForEach("li", func(_ int, li *colly.HTMLElement){
			var title string = li.ChildText("p[class=title]")
			var abstract string = li.ChildText("p[class=info]")
			var datetime string = li.ChildText("p[class=time]")
			var url string = li.ChildAttr("a", "href")
			if (len(title) > 5){
				if (strings.Index(abstract, "】") != -1){
					abstract = strings.Split(abstract, "】")[1]
				}
				var em EastMoney = EastMoney{title, abstract, url, datetime, "东方财富"}
				em.Strftime()
				news = append(news, em)
			}
		})
	})

	c.OnRequest(func(r *colly.Request) {})

	c.Visit(url)
	return news
}


/*为EastMoney结构体添加功能*/
// 时间格式化功能
func(e *EastMoney) Strftime(){
	var t string = e.Datetime
	t = strings.Replace(t, "月", "-", 1)
	t = strings.Replace(t, "日", "", 1)
	var now string = time.Now().String()
	var year string = now[0: 5]
	t = year + t
	e.Datetime = t
}

/*
 * 数据库相关内容
*/
// 数据库连接参数
type DB struct{
	user string
	pass string
	host string
	port int
	database string
	Instance *sqlx.DB
}

func (d *DB) Connect() {
	var db_url string = fmt.Sprintf("%v:%v@tcp(%v:%v)/%v?parseTime=true&loc=Local&charset=utf8", d.user, d.pass, d.host, d.port, d.database)
	var db *sqlx.DB
	db, err := sqlx.Connect("mysql", db_url)
	if (err != nil){
		panic(err)
	}
	d.Instance = db
}

func (d *DB) Insert(news EastMoney) {
	db := d.Instance
	tx := db.MustBegin()
	_, err := tx.NamedExec("INSERT INTO finance_news(title, abstract, url, savedate, source) VALUES(:title, :abstract, :url, :datetime, :source)", news)
	if err != nil {
		tx.Rollback()
	}else{
		tx.Commit()
	} 
}

func (d *DB) InsertAll(news []EastMoney) {
	for _, n := range(news){
		d.Insert(n)
	}
}

func (d *DB) Close() {
	d.Instance.Close()
}

// 从命令行获取数据库Host
func GetHost() string {
	args := os.Args
	if len(args) == 1{
		return "127.0.0.1"
	}else{
		return args[1]
	}
}