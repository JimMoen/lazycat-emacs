;;; init-markdown-mode.el --- Configure for markdown mode.

;; Filename: init-markdown-mode.el
;; Description: Configure for markdown mode.
;; Author: Andy Stewart <lazycat.manatee@gmail.com>
;; Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
;; Copyright (C) 2019, Andy Stewart, all rights reserved.
;; Created: 2019-09-22 08:25:25
;; Version: 0.1
;; Last-Updated: 2019-09-22 08:25:25
;;           By: Andy Stewart
;; URL: http://www.emacswiki.org/emacs/download/init-markdown-mode.el
;; Keywords:
;; Compatibility: GNU Emacs 26.3
;;
;; Features that might be required by this library:
;;
;;
;;

;;; This file is NOT part of GNU Emacs

;;; License
;;
;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 3, or (at your option)
;; any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program; see the file COPYING.  If not, write to
;; the Free Software Foundation, Inc., 51 Franklin Street, Fifth
;; Floor, Boston, MA 02110-1301, USA.

;;; Commentary:
;;
;; Configure for markdown mode.
;;

;;; Installation:
;;
;; Put init-markdown-mode.el to your load-path.
;; The load-path is usually ~/elisp/.
;; It's set in your ~/.emacs like this:
;; (add-to-list 'load-path (expand-file-name "~/elisp"))
;;
;; And the following to your ~/.emacs startup file.
;;
;; (require 'init-markdown-mode)
;;
;; No need more.

;;; Customize:
;;
;;
;;
;; All of the above can customize by:
;;      M-x customize-group RET init-markdown-mode RET
;;

;;; Change log:
;;
;; 2019/09/22
;;      * First released.
;;

;;; Acknowledgements:
;;
;;
;;

;;; TODO
;;
;;
;;

;;; Require
(require 'markdown-mode)
(require 'pangu-spacing)
(require 'deno-bridge-jieba)

(lazy-load-set-keys
 '(
   ("M-f" . deno-bridge-jieba-forward-word)
   ("M-b" . deno-bridge-jieba-backward-word)
   ("M-M" . deno-bridge-jieba-kill-word)
   ("M-N" . deno-bridge-jieba-backward-kill-word)
   )
 markdown-mode-map)

;;; Code:

(global-pangu-spacing-mode 1)

(dolist (hook (list
               'markdown-mode-hook
               ))
  (add-hook hook
            #'(lambda ()
                (set (make-local-variable 'pangu-spacing-real-insert-separtor) t)
                )))

(provide 'init-markdown-mode)

;;; init-markdown-mode.el ends here
