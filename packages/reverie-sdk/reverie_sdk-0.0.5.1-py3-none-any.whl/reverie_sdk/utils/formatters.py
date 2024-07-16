def duration_formatted(duration_secs: float) -> str:
    if duration_secs < 1e-6:
        return f"{duration_secs*1e6:.3f} microseconds"

    if duration_secs < 1e-3:
        return f"{duration_secs*1e3:.3f} milliseconds"

    if duration_secs < 60:
        return f"{duration_secs:.3f} seconds"

    if duration_secs < 3600:
        return f"{duration_secs/60:.3f} minutes"

    if duration_secs < (3600 * 24):
        return f"{duration_secs/3600:.3f} hours"

    return f"{duration_secs/(3600*24):.3f} days"
