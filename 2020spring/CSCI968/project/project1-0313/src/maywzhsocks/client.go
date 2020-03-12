package main

import (
	"flag"
	"log"

	socks5proxy "socks5/socks5proxy"
)

func main() {
	listenAddr := flag.String("local", ":8888", "Input server listen address(Default 8888):")
	serverAddr := flag.String("server", "", "Input server listen address:")
	passwd := flag.String("passwd", "123456", "Input server proxy password:")
	encrytype := flag.String("type", "random", "Input encryption type:")
	recvHTTPProto := flag.String("recv", "http", "use http or sock5 protocol(default http):")
	flag.Parse()
	if *serverAddr == "" {
		log.Fatal("请输入正确的远程地址")
	}
	log.Println("客户端正在启动...")
	log.Println(&recvHTTPProto)
	socks5proxy.Client(*listenAddr, *serverAddr, *encrytype, *passwd, *recvHTTPProto)
}
