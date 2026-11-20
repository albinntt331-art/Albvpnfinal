"""Albin-vpn v8 Windows Config Builder — Rock-solid sing-box 1.14 Wintun & Xray-core."""
import json
import socket
import time


def resolve_host_ipv4(host: str) -> str:
    try:
        return socket.gethostbyname(host)
    except Exception:
        return host


def choose_core(profile: dict, vpn_mode: str, is_admin: bool) -> str:
    net = (profile.get("params", {}).get("type") or profile.get("params", {}).get("net") or "tcp").lower()
    # Upstream sing-box does not support XHTTP/splithttp -> use Xray for XHTTP
    if net in ("xhttp", "splithttp"):
        return "xray"
    if is_admin:
        return "sing-box"
    if profile.get("protocol") in ("hysteria2", "wireguard", "tuic"):
        return "sing-box"
    return "xray"


def build_singbox_config(profile: dict, settings: dict, use_tun: bool = True) -> str:
    p = profile.get("params", {})
    proto = profile.get("protocol", "vless")
    mode = settings.get("vpn_mode", "proxy_apps")
    policy = settings.get("per_app_policy", "only_selected")
    apps = [a.strip() for a in settings.get("selected_apps", []) if a.strip()]
    resolved_ip = resolve_host_ipv4(profile["address"])

    inbounds = [
        {"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 10809}
    ]
    if use_tun:
        # IPv4-only by default so Wintun auto_route never fails on IPv4-only Windows networks!
        addrs = ["172.19.0.1/30"]
        if settings.get("ipv6", False):
            addrs.append("fdfe:dcba:9876::1/126")
        inbounds.insert(0, {
            "type": "tun",
            "tag": "tun-in",
            "interface_name": f"AlbinVPN_{int(time.time()) % 100000}",
            "address": addrs,
            "mtu": 1400,
            "auto_route": True,
            "strict_route": True,
        })

    proxy = {"tag": "proxy", "server": resolved_ip, "server_port": profile["port"]}
    if proto == "vless":
        proxy["type"] = "vless"
        proxy["uuid"] = p.get("user", "")
        proxy["packet_encoding"] = "xudp"
        if p.get("flow"):
            proxy["flow"] = p["flow"]
        sec = p.get("security") or p.get("tls") or "none"
        if sec in ("reality", "tls"):
            tls = {
                "enabled": True,
                "server_name": p.get("sni") or profile["address"],
                "utls": {"enabled": True, "fingerprint": p.get("fp", "chrome")},
            }
            if sec == "reality":
                tls["reality"] = {"enabled": True, "public_key": p.get("pbk", ""), "short_id": p.get("sid", "")}
            proxy["tls"] = tls
        net = p.get("type") or p.get("net") or "tcp"
        if net == "ws":
            proxy["transport"] = {"type": "ws", "path": p.get("path", "/"), "headers": {"Host": p.get("host") or profile["address"]}}
        elif net == "grpc":
            proxy["transport"] = {"type": "grpc", "service_name": p.get("serviceName", "")}
    elif proto == "hysteria2":
        proxy["type"] = "hysteria2"
        proxy["password"] = p.get("user", "")
        proxy["tls"] = {"enabled": True, "server_name": p.get("sni") or profile["address"], "insecure": p.get("insecure") == "1"}
    elif proto == "trojan":
        proxy["type"] = "trojan"
        proxy["password"] = p.get("user", "")
        proxy["tls"] = {"enabled": True, "server_name": p.get("sni") or profile["address"]}
    elif proto == "vmess":
        proxy["type"] = "vmess"
        proxy["uuid"] = p.get("id", "")
        proxy["security"] = p.get("scy", "auto")
    else:
        proxy["type"] = "shadowsocks"
        proxy["method"] = p.get("method", "aes-256-gcm")
        proxy["password"] = p.get("password", "")

    route_rules = [
        {"action": "sniff"},
        {"protocol": "dns", "action": "hijack-dns"},
    ]
    if not settings.get("ipv6", False):
        route_rules.append({"ip_version": 6, "action": "reject"})

    final_out = "proxy"
    if mode == "proxy_apps" and apps:
        if policy == "only_selected":
            route_rules.append({"process_name": apps, "outbound": "proxy"})
            final_out = "direct"
        else:
            route_rules.append({"process_name": apps, "outbound": "direct"})
            final_out = "proxy"

    cfg = {
        "log": {"level": "info", "timestamp": True},
        "dns": {
            "servers": [
                {"tag": "remote", "type": "tcp", "server": "1.1.1.1", "detour": "proxy"},
                {"tag": "local", "type": "local"},
            ],
            "final": "remote",
            "strategy": "ipv4_only" if not settings.get("ipv6", False) else "prefer_ipv4",
        },
        "inbounds": inbounds,
        "outbounds": [
            proxy,
            {"type": "direct", "tag": "direct"},
        ],
        "route": {
            "auto_detect_interface": True,
            "default_domain_resolver": "local",
            "final": final_out,
            "rules": route_rules,
        },
    }
    return json.dumps(cfg, indent=2, ensure_ascii=False)


def build_xray_config(profile: dict, settings: dict) -> str:
    p = profile.get("params", {})
    proto = profile.get("protocol", "vless")
    resolved_ip = resolve_host_ipv4(profile["address"])
    sniffing = {"enabled": True, "destOverride": ["http", "tls", "quic"]}

    outbound = {"tag": "proxy", "protocol": proto}
    if proto == "vless":
        user = {"id": p.get("user", ""), "encryption": p.get("encryption", "none")}
        if p.get("flow"):
            user["flow"] = p["flow"]
        outbound["settings"] = {"vnext": [{"address": resolved_ip, "port": profile["port"], "users": [user]}]}
    elif proto == "trojan":
        outbound["settings"] = {"servers": [{"address": resolved_ip, "port": profile["port"], "password": p.get("user", "")}]}
    elif proto == "vmess":
        outbound["settings"] = {"vnext": [{"address": resolved_ip, "port": profile["port"], "users": [{"id": p.get("id", ""), "security": p.get("scy", "auto")}]}]}
    else:
        outbound["protocol"] = "shadowsocks"
        outbound["settings"] = {"servers": [{"address": resolved_ip, "port": profile["port"], "method": p.get("method", "aes-256-gcm"), "password": p.get("password", "")}]}

    net = p.get("type") or p.get("net") or "tcp"
    if net == "raw":
        net = "tcp"
    sec = p.get("security") or p.get("tls") or "none"
    stream = {"network": net, "security": sec}
    if sec == "reality":
        stream["realitySettings"] = {
            "serverName": p.get("sni") or profile["address"], "fingerprint": p.get("fp", "chrome"),
            "publicKey": p.get("pbk", ""), "shortId": p.get("sid", ""), "spiderX": p.get("spx", "/"),
        }
    elif sec == "tls":
        stream["tlsSettings"] = {"serverName": p.get("sni") or profile["address"], "fingerprint": p.get("fp", "chrome")}
    if net == "ws":
        stream["wsSettings"] = {"path": p.get("path", "/"), "headers": {"Host": p.get("host") or profile["address"]}}
    elif net == "grpc":
        stream["grpcSettings"] = {"serviceName": p.get("serviceName", "")}
    elif net in ("xhttp", "splithttp"):
        stream["xhttpSettings"] = {"path": p.get("path", "/")}
        if p.get("host"):
            stream["xhttpSettings"]["host"] = p["host"]
    outbound["streamSettings"] = stream

    cfg = {
        "log": {"loglevel": "info"},
        "dns": {"servers": ["1.1.1.1", "8.8.8.8"], "queryStrategy": "UseIPv4"},
        "inbounds": [
            {"tag": "socks-in", "port": 10808, "listen": "127.0.0.1", "protocol": "socks", "sniffing": sniffing, "settings": {"udp": True}},
            {"tag": "http-in", "port": 10809, "listen": "127.0.0.1", "protocol": "http", "sniffing": sniffing},
        ],
        "outbounds": [outbound, {"tag": "direct", "protocol": "freedom"}, {"tag": "block", "protocol": "blackhole"}],
        "routing": {"domainStrategy": "AsIs", "rules": [{"type": "field", "network": "tcp,udp", "outboundTag": "proxy"}]},
    }
    return json.dumps(cfg, indent=2, ensure_ascii=False)
