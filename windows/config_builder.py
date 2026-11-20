"""Albin-vpn v8.2 Windows Config Builder — Rock-solid sing-box 1.14 gVisor Wintun & Xray-core."""
import ipaddress
import json
import socket
import time


def resolve_host_ipv4(host: str) -> str:
    try:
        return socket.gethostbyname(host)
    except Exception:
        return host


def _is_ipv4(addr: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(addr), ipaddress.IPv4Address)
    except Exception:
        return False


def _expand_process_names(apps: list[str]) -> list[str]:
    out = []
    seen = set()
    for a in apps:
        name = a.strip()
        if not name:
            continue
        variants = [name, name.lower(), name[0].upper() + name[1:].lower() if len(name) > 1 else name]
        for v in variants:
            if v not in seen:
                seen.add(v)
                out.append(v)
    return out


def choose_core(profile: dict, vpn_mode: str, is_admin: bool) -> str:
    net = (profile.get("params", {}).get("type") or profile.get("params", {}).get("net") or "tcp").lower()
    # Upstream sing-box does not support XHTTP/splithttp -> use Xray (chained behind sing-box TUN when Admin)
    if net in ("xhttp", "splithttp"):
        return "xray"
    if is_admin:
        return "sing-box"
    if profile.get("protocol") in ("hysteria2", "wireguard", "tuic"):
        return "sing-box"
    return "xray"


def build_singbox_config(
    profile: dict,
    settings: dict,
    use_tun: bool = True,
    upstream_socks_port: int | None = None,
) -> str:
    p = profile.get("params", {})
    proto = profile.get("protocol", "vless")
    mode = settings.get("vpn_mode", "proxy_apps")
    policy = settings.get("per_app_policy", "only_selected")
    apps = _expand_process_names(settings.get("selected_apps", []))
    resolved_ip = resolve_host_ipv4(profile["address"])

    inbounds = [
        {"type": "mixed", "tag": "mixed-in", "listen": "127.0.0.1", "listen_port": 10809}
    ]
    if use_tun:
        addrs = ["172.19.0.1/30"]
        if settings.get("ipv6", False):
            addrs.append("fdfe:dcba:9876::1/126")
        tun_in = {
            "type": "tun",
            "tag": "tun-in",
            "interface_name": f"AlbinVPN_{int(time.time()) % 100000}",
            "address": addrs,
            "mtu": 1400,
            "auto_route": True,
            "strict_route": (mode == "tun"),
            # CRITICAL: gvisor stack handles TCP+UDP in user-space without Windows Firewall loopback blocks!
            "stack": "gvisor",
        }
        if _is_ipv4(resolved_ip):
            tun_in["route_exclude_address"] = [f"{resolved_ip}/32"]
        inbounds.insert(0, tun_in)

    if upstream_socks_port is not None:
        proxy = {
            "type": "socks",
            "tag": "proxy",
            "server": "127.0.0.1",
            "server_port": upstream_socks_port,
        }
    else:
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
        # Always route local mixed proxy inbound (Dual-IP check & proxy clients) through VPN
        {"inbound": ["mixed-in"], "outbound": "proxy"},
        # Keep local LAN & loopback (including Xray chain 127.0.0.1:10808) reachable
        {"ip_is_private": True, "outbound": "direct"},
    ]
    if not settings.get("ipv6", False):
        route_rules.append({"ip_version": 6, "action": "reject"})

    dns_rules = []
    dns_final = "remote"
    final_out = "proxy"

    if mode == "proxy_apps" and apps:
        if policy == "only_selected":
            route_rules.append({"process_name": apps, "outbound": "proxy"})
            final_out = "direct"
            dns_rules.append({"process_name": apps, "server": "remote"})
            dns_final = "local"
        else:
            route_rules.append({"process_name": apps, "outbound": "direct"})
            final_out = "proxy"
            dns_rules.append({"process_name": apps, "server": "local"})
            dns_final = "remote"

    dns_cfg = {
        "servers": [
            {"tag": "remote", "type": "tcp", "server": "1.1.1.1", "detour": "proxy"},
            {"tag": "local", "type": "local"},
        ],
        "final": dns_final,
        "strategy": "ipv4_only" if not settings.get("ipv6", False) else "prefer_ipv4",
    }
    if dns_rules:
        dns_cfg["rules"] = dns_rules

    cfg = {
        "log": {"level": "info", "timestamp": True},
        "dns": dns_cfg,
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
