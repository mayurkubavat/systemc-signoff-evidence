# Review: feature/cmdline-config-bitstream
Commit reviewed: parent of 27c242a64509b01c283e7a99c880d98788af099c (amended after review to act on the findings below)
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- macOS 72/79, Linux 78/79, known failures only. string_to_integral has two callers only. Compiles with UVM_MAX_STREAMBITS 32/64/128/4096.

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| F2 | Decimal values >= 2^63 rejected although doc says up to 64 bits | medium | Acted on: bitstream values without a minus sign use the full 64 bits; test added |
| F3 | Values wider than 64 bits get the generic 'not an integral value' error | low | Noted: limit is documented |
| F4 | Negative values are 64-bit, not sign-extended over the bitstream width; -'h1 rejected | low | Noted: same as +uvm_set_config_int |
| F5 | Underscore after a sign (-_1) and trailing/double underscores accepted, inconsistent with the stated rule | low | Acted on: an underscore before the first digit is rejected also after a sign; rule documented as 'underscores after the first digit are ignored' |

## Unproven / design
- int and bitstream settings of one field live in separate stores (SV has one); an unparsable value is a UVM_ERROR (SV ignores it).

## Verdict
Ready after F2 and F5 fixes (applied, regression rerun).
