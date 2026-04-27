FROM alpine:3.20

RUN apk add --no-cache bash curl iptables ipset nginx haproxy jq python3

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY haproxy/haproxy.cfg /etc/haproxy/haproxy.cfg
RUN printf '\n' >> /etc/haproxy/haproxy.cfg

COPY scripts/entrypoint.sh /entrypoint.sh
COPY scripts/apply_bans.sh /apply_bans.sh
COPY scripts/whitelist.sh /whitelist.sh


RUN chmod +x /entrypoint.sh /apply_bans.sh /whitelist.sh

EXPOSE 80 2222
ENTRYPOINT ["/entrypoint.sh"]