# Frequenz Reporting API Release Notes

## Summary

- Metric source options

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

- A new field, `MetricSourceOptions` has been added to the `StreamFilter` message, allowing users to give specific sources for a given metric.
  Multiples of the same metric can exist, in which case they are "tagged" with the source they come from. The metric source options allows
  the user to specify one or multiple tags.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
