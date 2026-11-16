How to work (follow these steps in order):

1. Requirement. Restate in two or three lines what must change, and the
   observable behaviour or exact text the task asks for. Locate the code with
   one or two searches (grep, find). Do not read whole directories.
2. Reproduce. Find the existing regression test closest to the task, or write
   a small new one (a test folder with test.cpp and golden/test.log, like its
   neighbours). Build and run only that test ({run_hint}) and watch it fail
   for the reason the task describes.
3. Change. Make the smallest source change that resolves the task. Start
   editing by your 15th turn at the latest; exploring longer is the most
   common reason for running out of turns.
4. Verify. Run the test again until it passes. When it compares against a
   golden log, read the diff line by line: message ids, wording, spacing and
   counts must match exactly.
5. Regression. Run the tests of the affected area once ({regression_hint})
   and fix anything you broke.
6. Finish. Once the tests pass, stop and give a short summary of the change.

Rules:
- New UVM classes, methods and messages follow the UVM reference
  implementation in SystemVerilog, whose source is at {uvm_ref}: read the
  matching .svh file there for behaviour, report ids and message text.
- Do not search the web or fetch URLs; everything you need is in this
  checkout and the reference source.
- You have at most {max_turns} turns. Batch related reads into one command,
  rebuild only the target you need, and never rebuild the whole tree twice.
