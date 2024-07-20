#!/usr/bin/env python
#
# Copyright (c) James Cherti
# URL: https://github.com/jamescherti/elispcomp
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
#
"""Lisp code that recursively byte-compile and native-compile .el files."""

LISP_CODE = """
(progn
  (defun my-add-load-paths (paths-string)
    "Add directories specified in PATHS-STRING to `load-path`.
PATHS-STRING should be a string containing directories separated by newline
characters."
    (let ((paths (split-string paths-string "\n" t)))
      (dolist (path paths)
        (let ((default-directory (expand-file-name path)))
          (normal-top-level-add-subdirs-to-load-path)))))

  (setq byte-compile-verbose nil)
  (let* ((default-directory (getenv "EMACS_BYTE_COMP_DIR"))
         (load-path-list (getenv "EMACS_LOAD_PATH_LIST"))
         (eln-cache-dir (getenv "EMACS_ELN_CACHE_DIR"))
         (jobs (getenv "EMACS_NATIVE_COMP_ASYNC_JOBS_NUMBER"))
         (byte-comp-enabled
          (/= 0 (string-to-number (getenv "EMACS_BYTE_COMP_ENABLED"))))
         (native-comp-enabled
          (and (/= 0 (string-to-number (getenv "EMACS_NATIVE_COMP_ENABLED")))
               (featurep 'native-compile)
               (fboundp 'native-comp-available-p)
               (native-comp-available-p))))
    ;; SET ELN-CACHE DIR
    (when (and native-comp-enabled (not (string= eln-cache-dir "")))
      (cond ((fboundp 'startup-redirect-eln-cache) ; Emacs >= 28
             (startup-redirect-eln-cache eln-cache-dir))
            ((boundp 'native-comp-eln-load-path)
             (setcar native-comp-eln-load-path
                     (expand-file-name
                      (convert-standard-filename eln-cache-dir)
                      user-emacs-directory)))
            (t (error "Cannot change the eln-cache-dir directory"))))

    ;; SHOW MESSAGES
    (message "[INFO] Recursively compile the directory: %s"
     default-directory)
    (message "[INFO] Byte comp enabled: %s" byte-comp-enabled)
    (message "[INFO] Native comp enabled: %s" native-comp-enabled)
    (message "[INFO] Jobs: %s" jobs)
    (message "[INFO] Emacs user directory: %s" user-emacs-directory)
    (message "[INFO] eln-cache directory: %s\n" eln-cache-dir)
    (message "[INFO] Load path directories:\n%s\n" load-path-list)

    ;; LOAD DIRECTORIES
    (my-add-load-paths load-path-list)

    ;; BYTE-COMP
    (when byte-comp-enabled
      (message "[TASK] Byte compile")
      (byte-recompile-directory default-directory 0))

    ;; NATIVE-COMP
    (when native-comp-enabled
      (message "[TASK] Native compile")
      (setq native-comp-async-report-warnings-errors t)
      (setq native-comp-warning-on-missing-source t)
      (when (and jobs (not (string= jobs "")))
        (setq native-comp-async-jobs-number (string-to-number jobs)))
      (setq native-comp-deferred-compilation nil)
      (setq package-native-compile nil)
      (native-compile-async default-directory 'recursively)
      (while comp-files-queue
        (sleep-for 0.25)))))
"""
