What results are given when a battery is not present?

Idea (for now): show output; find command that successfully detects a battery

# Raspi

```
{"is_discharging": true, "is_charging": true, "percent": null, "minutes_to_empty": null, "minutes_to_full": null, "capacity": null, "design_capacity": null}
```

`upower -d | grep 'power supply' | grep -qv 'yes'; echo $?`