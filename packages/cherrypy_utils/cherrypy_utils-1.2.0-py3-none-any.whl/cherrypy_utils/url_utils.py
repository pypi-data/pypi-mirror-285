def combine_url(domain, *parts):
    if domain == "/":
        return "/" + "/".join(parts)

    joined = "/" + domain.strip("/") + "/" + "/".join(parts)

    if joined.startswith("//"):
        joined = joined[1:]

    while joined.endswith("/"):
        joined = joined[:-1]

    return joined
