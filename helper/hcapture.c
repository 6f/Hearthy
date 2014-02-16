#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>

#include <time.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "nids.h"

#define int_ntoa(x)	inet_ntoa(*((struct in_addr *)&x))

#define EV_NEW_CONNECTION 0
#define EV_CLOSE 1
#define EV_DATA 2

#define REPORT_HEADER_VERSION "HCaptureV0"

void
print_usage(char *name, FILE *out) {
    fprintf(out, "Usage: %s [-i iface] <out>\n", name);
}

struct conn_params {
    int stream_id;
};

#define MAX_BUF 1024

FILE* outfile = NULL;
int stream_count = 0;
uint8_t header_buf[MAX_BUF];
int64_t reference_ts;

unsigned int
write_uint64(uint8_t *buf, unsigned int offset, uint64_t arg) {
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff;
    return offset;
}

unsigned int
write_uint32(uint8_t *buf, unsigned int offset, unsigned int arg) {
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff;
    return offset;
}

unsigned int
write_uint16(uint8_t *buf, unsigned int offset, unsigned int arg) {
    buf[offset++] = arg & 0xff; arg >>= 8;
    buf[offset++] = arg & 0xff;
    return offset;
}

unsigned int
write_uint8(uint8_t *buf, unsigned int offset, unsigned int arg) {
    buf[offset++] = arg & 0xff;
    return offset;
}

// Returns a timestamp in milliseconds, should only be used
// for relative calculations (i.e. durations).
// This timestamp *should* be monotonic.
int64_t
get_relative_timestamp(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &ts) != 0) {
        return INT64_MIN;
    }
    return ((int64_t)ts.tv_sec) * 1000 + (ts.tv_nsec / 1000000);
}

unsigned int
write_relative_timestamp(uint8_t *buf, unsigned int offset) {
    int64_t diff = get_relative_timestamp() - reference_ts;
    return write_uint64(buf, offset, (uint64_t)diff);
}

void
report_write_header(int64_t timestamp) {
    unsigned int offset = sizeof(REPORT_HEADER_VERSION);
    strcpy((char*)header_buf, REPORT_HEADER_VERSION);
    offset = write_uint64(header_buf, offset, (uint64_t)timestamp);

    // TODO: check for errors
    fwrite(header_buf, 1, offset, outfile);
    fflush(outfile);
}

void
report_new_connection(struct conn_params * params, struct tuple4 * addr) {
    unsigned int offset = 4;
    offset = write_relative_timestamp(header_buf, offset);
    offset = write_uint8(header_buf, offset, EV_NEW_CONNECTION);
    offset = write_uint32(header_buf, offset, params->stream_id);
    offset = write_uint32(header_buf, offset, ntohl(addr->saddr));
    offset = write_uint16(header_buf, offset, addr->source);
    offset = write_uint32(header_buf, offset, ntohl(addr->daddr));
    offset = write_uint16(header_buf, offset, addr->dest);
    write_uint32(header_buf, 0, offset);

    // TODO: check for errors
    fwrite(header_buf, 1, offset, outfile);
    fflush(outfile);
}

void
report_close(struct conn_params * params) {
    unsigned int offset = 4;
    offset = write_relative_timestamp(header_buf, offset);
    offset = write_uint8(header_buf, offset, EV_CLOSE);
    offset = write_uint32(header_buf, offset, params->stream_id);
    write_uint32(header_buf, 0, offset);

    // TODO: check for errors
    fwrite(header_buf, 1, offset, outfile);
    fflush(outfile);
}

void
report_data(struct conn_params * params, int who, char * buf, int count) {
    unsigned int offset = 4;
    offset = write_relative_timestamp(header_buf, offset);
    offset = write_uint8(header_buf, offset, EV_DATA);
    offset = write_uint32(header_buf, offset, params->stream_id);
    offset = write_uint8(header_buf, offset, who);
    write_uint32(header_buf, 0, offset + count);

    // TODO: check for errors
    fwrite(header_buf, 1, offset, outfile);
    fwrite(buf, 1, count, outfile);
    fflush(outfile);
}

void
tcp_callback(struct tcp_stream *a_tcp, void ** param) {
    struct conn_params * params = *param;
    if (params == NULL && a_tcp->nids_state != NIDS_JUST_EST) {
        printf("Can this even happen?\n");
        return;
    }

    if (a_tcp->nids_state == NIDS_JUST_EST) {
        *param = NULL;

        printf("Source: %s:%u\n", int_ntoa(a_tcp->addr.saddr), a_tcp->addr.source);
        printf("Dest: %s:%u\n", int_ntoa(a_tcp->addr.daddr), a_tcp->addr.dest);

        if (a_tcp->addr.dest == 1119) {
            params = malloc(sizeof(struct conn_params));
            if (params == NULL) {
                fprintf(stderr, "Warn: malloc failed!\n");
            } else {
                *param = params;
                params->stream_id = stream_count++;

                report_new_connection(params, &a_tcp->addr);

                a_tcp->client.collect++;
                a_tcp->server.collect++;

                printf("Started recording stream id=%d\n", params->stream_id);
            }
        }
    } else if (a_tcp->nids_state == NIDS_CLOSE || a_tcp->nids_state == NIDS_RESET) {
        printf("Stream id=%d closed\n", params->stream_id);
        report_close(params);
        free(params);
    } else if (a_tcp->nids_state == NIDS_DATA) {
        if (a_tcp->client.count_new) {
            report_data(params, 1, a_tcp->client.data, a_tcp->client.count_new);
        } else if (a_tcp->server.count_new) {
            report_data(params, 0, a_tcp->server.data, a_tcp->server.count_new);
        } else {
            printf("Warning: NIDS_DATA occured without new data\n");
        }
    }
}

struct {
    char * device;
    char * error;
    char * outfn;
    int showhelp;
} opts;

void
parse_opts(char *argv[]) {
    char * cur = *argv;
    char * next = NULL;

    while (cur != NULL) {
        next = *(++argv);

        if (strcmp(cur, "-i") == 0) {
            if (next == NULL) {
                opts.error = "Options -i requires an argument!";
                return;
            }
            opts.device = next;
            next = *(++argv);
        } else {
            if (opts.outfn == NULL) {
                opts.outfn = cur;
            } else {
                opts.error = "Trailing positional argument";
                return;
            }
        }
        cur = next;
    }
    if (opts.outfn == NULL) {
        opts.error = "Output filename is required";
    }
}

int
main(int argc, char *argv[]) {
    // initialize options
    opts.device = NULL;
    opts.error = NULL;
    opts.outfn = NULL;
    opts.showhelp = 0;

    // parse options
    parse_opts(argv+1);

    if (opts.error) {
        fprintf(stderr, "Error: %s\n", opts.error);
        print_usage(argv[0], stderr);
        exit(1);
    }

    // Open output file
    outfile = fopen(opts.outfn, "wb");
    if (outfile == NULL) {
        perror("fopen");
        return 1;
    }

    // Initialize nids
    nids_params.device = opts.device;
    nids_params.promisc = 0;
    if (!nids_init()) {
        fprintf(stderr, "%s\n", nids_errbuf);
        return 1;
    }

    // Disable checksum checking
    struct nids_chksum_ctl nochksumchk;
    nochksumchk.netaddr = 0;
    nochksumchk.mask = 0;
    nochksumchk.action = NIDS_DONT_CHKSUM;

    nids_register_chksum_ctl(&nochksumchk, 1);

    // Get unix timestamp and monotonic timestamp
    int64_t timestamp = (int64_t)time(NULL);

    reference_ts = get_relative_timestamp();
    
    if (reference_ts == INT64_MIN) {
        perror("clock_gettime");
        return 1;
    }

    // write report header
    report_write_header(timestamp);

    // Start main loop
    nids_register_tcp(tcp_callback);
    nids_run();

    fclose(outfile);
    return 0;
}
