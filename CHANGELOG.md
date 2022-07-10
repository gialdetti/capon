# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
* Data: Up-to-date metadata.
* Visualization: altair plotter.
* Tests: tox testing.
* API: yahoo finance history API.

## [0.0.6] - 2022-06-02
### Added
* API: Portfolio - support anchor time for performance computations.
* API: Utils - `normalize_values`.
* Visualization - plot history.
* Maintenance: Update to python 3.9
### Fixed
* Update to new Yahoo API (user-agent).

## [0.0.5] - 2020-12-31
### Added
* CHANGELOG.md file.
* Examples: Interactive example for using capon's metadata api -
  **"Analyzing the Sector-level Crash and Rebound"**.
* API: OTC backend - screener.
* API: Nasdaq backend - extended API and screener.

## [0.0.4] - 2020-08-30
### Added
- Data: Metadata cache for all current stocks.

## [0.0.3] - 2020-07-23
### Added
- API: Fetch realtime stock metadata from NASDAQ site.
- Visualization: capon template for plotly.
- DOC: Update README.md with new examples.

## [0.0.2] - 2020-06-14
### Added
- API: Expose generic `capon.stock(.)` to fetch realtime stock price data.
- Feature: Support multiple timezones.
- Data: Metadate for stock indexes.  
- Examples: Interactive example for using capon's stock api and market indexes. Analyzing
  **"2020 Stock Market Crash and Rebound Amid Coronavirus"**.

## [0.0.1] - 2020-05-19
### Added
- API: Portfolio management and monitoring.
- API: Yahoo Finance backend for fetch realtime stock price data. 
- Examples: Interactive example for using capon's portfolio **"My Stock Portfolio Performance"**.
- DOC: README file.

[unreleased]: https://github.com/gialdetti/capon/compare/2d2c32e...HEAD
[0.0.6]: https://github.com/gialdetti/capon/compare/f74d79e...2d2c32e
[0.0.5]: https://github.com/gialdetti/capon/compare/3b47851...f74d79e
[0.0.4]: https://github.com/gialdetti/capon/compare/fa4ab8e...3b47851
[0.0.3]: https://github.com/gialdetti/capon/compare/d03b7b9...fa4ab8e
[0.0.2]: https://github.com/gialdetti/capon/compare/faf8aef...d03b7b9
[0.0.1]: https://github.com/gialdetti/capon/compare/3125ac6...faf8aef

