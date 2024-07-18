import {
  A,
  AIM_FORM_LAYOUT,
  AIM_OPTION_PARENT_COMPONENT,
  AIM_SELECT_CONTEXT,
  ActiveDescendantKeyManager,
  AimFormLayoutComponent,
  AimFormLayoutControl,
  AimIconComponent,
  AimOptgroupComponent,
  AimOptionComponent,
  AimOptionModule,
  AimSelectContext,
  AimSelectFieldSize,
  AimSelectFieldWidth,
  Attribute,
  CdkConnectedOverlay,
  CdkOverlayOrigin,
  CdkScrollableModule,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  CommonModule,
  Component,
  ContentChild,
  ContentChildren,
  DOCUMENT,
  DOWN_ARROW,
  Directionality,
  Directive,
  ENTER,
  ElementRef,
  ErrorStateMatcher,
  EventEmitter,
  FactoryTarget,
  FormGroupDirective,
  HostBinding,
  Inject,
  Injectable,
  InjectionToken,
  Input,
  LEFT_ARROW,
  LiveAnnouncer,
  MAT_FORM_FIELD,
  MAT_OPTGROUP,
  MAT_OPTION_PARENT_COMPONENT,
  MatCommonModule,
  MatFormField,
  MatFormFieldControl,
  MatFormFieldModule,
  MatOption,
  MatOptionModule,
  NgClass,
  NgControl,
  NgForm,
  NgIf,
  NgModule,
  NgZone,
  Optional,
  Output,
  Overlay,
  OverlayModule,
  RIGHT_ARROW,
  SPACE,
  SelectOptionHeight,
  SelectionModel,
  Self,
  Subject,
  TranslateService,
  UP_ARROW,
  Validators,
  ViewChild,
  ViewEncapsulation$1,
  ViewportRuler,
  _ErrorStateTracker,
  __decorate,
  _countGroupLabelsBeforeOption,
  _getOptionScrollPosition,
  addAriaReferencedId,
  animate,
  animateChild,
  booleanAttribute,
  catchError,
  core_exports,
  defer,
  distinctUntilChanged,
  filter,
  forkJoin,
  hasModifierKey,
  inject,
  isEqual_default,
  isNil_default,
  map,
  merge,
  numberAttribute,
  of,
  query,
  removeAriaReferencedId,
  startWith,
  state,
  style,
  switchMap,
  take,
  takeUntil,
  tap,
  transition,
  trigger,
  ɵɵngDeclareClassMetadata,
  ɵɵngDeclareComponent,
  ɵɵngDeclareDirective,
  ɵɵngDeclareFactory,
  ɵɵngDeclareInjectable,
  ɵɵngDeclareInjector,
  ɵɵngDeclareNgModule
} from "./chunk-PWJHAR3G.js";
import {
  __async,
  __commonJS,
  __require,
  __spreadValues,
  __toESM
} from "./chunk-SJP7IFL7.js";

// node_modules/localforage/dist/localforage.js
var require_localforage = __commonJS({
  "node_modules/localforage/dist/localforage.js"(exports, module) {
    (function(f) {
      if (typeof exports === "object" && typeof module !== "undefined") {
        module.exports = f();
      } else if (typeof define === "function" && define.amd) {
        define([], f);
      } else {
        var g;
        if (typeof window !== "undefined") {
          g = window;
        } else if (typeof global !== "undefined") {
          g = global;
        } else if (typeof self !== "undefined") {
          g = self;
        } else {
          g = this;
        }
        g.localforage = f();
      }
    })(function() {
      var define2, module2, exports2;
      return function e(t, n, r) {
        function s(o2, u) {
          if (!n[o2]) {
            if (!t[o2]) {
              var a = typeof __require == "function" && __require;
              if (!u && a)
                return a(o2, true);
              if (i)
                return i(o2, true);
              var f = new Error("Cannot find module '" + o2 + "'");
              throw f.code = "MODULE_NOT_FOUND", f;
            }
            var l = n[o2] = { exports: {} };
            t[o2][0].call(l.exports, function(e2) {
              var n2 = t[o2][1][e2];
              return s(n2 ? n2 : e2);
            }, l, l.exports, e, t, n, r);
          }
          return n[o2].exports;
        }
        var i = typeof __require == "function" && __require;
        for (var o = 0; o < r.length; o++)
          s(r[o]);
        return s;
      }({ 1: [function(_dereq_, module3, exports3) {
        (function(global2) {
          "use strict";
          var Mutation = global2.MutationObserver || global2.WebKitMutationObserver;
          var scheduleDrain;
          {
            if (Mutation) {
              var called = 0;
              var observer = new Mutation(nextTick);
              var element = global2.document.createTextNode("");
              observer.observe(element, {
                characterData: true
              });
              scheduleDrain = function() {
                element.data = called = ++called % 2;
              };
            } else if (!global2.setImmediate && typeof global2.MessageChannel !== "undefined") {
              var channel = new global2.MessageChannel();
              channel.port1.onmessage = nextTick;
              scheduleDrain = function() {
                channel.port2.postMessage(0);
              };
            } else if ("document" in global2 && "onreadystatechange" in global2.document.createElement("script")) {
              scheduleDrain = function() {
                var scriptEl = global2.document.createElement("script");
                scriptEl.onreadystatechange = function() {
                  nextTick();
                  scriptEl.onreadystatechange = null;
                  scriptEl.parentNode.removeChild(scriptEl);
                  scriptEl = null;
                };
                global2.document.documentElement.appendChild(scriptEl);
              };
            } else {
              scheduleDrain = function() {
                setTimeout(nextTick, 0);
              };
            }
          }
          var draining;
          var queue = [];
          function nextTick() {
            draining = true;
            var i, oldQueue;
            var len = queue.length;
            while (len) {
              oldQueue = queue;
              queue = [];
              i = -1;
              while (++i < len) {
                oldQueue[i]();
              }
              len = queue.length;
            }
            draining = false;
          }
          module3.exports = immediate;
          function immediate(task) {
            if (queue.push(task) === 1 && !draining) {
              scheduleDrain();
            }
          }
        }).call(this, typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {});
      }, {}], 2: [function(_dereq_, module3, exports3) {
        "use strict";
        var immediate = _dereq_(1);
        function INTERNAL() {
        }
        var handlers = {};
        var REJECTED = ["REJECTED"];
        var FULFILLED = ["FULFILLED"];
        var PENDING = ["PENDING"];
        module3.exports = Promise2;
        function Promise2(resolver) {
          if (typeof resolver !== "function") {
            throw new TypeError("resolver must be a function");
          }
          this.state = PENDING;
          this.queue = [];
          this.outcome = void 0;
          if (resolver !== INTERNAL) {
            safelyResolveThenable(this, resolver);
          }
        }
        Promise2.prototype["catch"] = function(onRejected) {
          return this.then(null, onRejected);
        };
        Promise2.prototype.then = function(onFulfilled, onRejected) {
          if (typeof onFulfilled !== "function" && this.state === FULFILLED || typeof onRejected !== "function" && this.state === REJECTED) {
            return this;
          }
          var promise = new this.constructor(INTERNAL);
          if (this.state !== PENDING) {
            var resolver = this.state === FULFILLED ? onFulfilled : onRejected;
            unwrap(promise, resolver, this.outcome);
          } else {
            this.queue.push(new QueueItem(promise, onFulfilled, onRejected));
          }
          return promise;
        };
        function QueueItem(promise, onFulfilled, onRejected) {
          this.promise = promise;
          if (typeof onFulfilled === "function") {
            this.onFulfilled = onFulfilled;
            this.callFulfilled = this.otherCallFulfilled;
          }
          if (typeof onRejected === "function") {
            this.onRejected = onRejected;
            this.callRejected = this.otherCallRejected;
          }
        }
        QueueItem.prototype.callFulfilled = function(value) {
          handlers.resolve(this.promise, value);
        };
        QueueItem.prototype.otherCallFulfilled = function(value) {
          unwrap(this.promise, this.onFulfilled, value);
        };
        QueueItem.prototype.callRejected = function(value) {
          handlers.reject(this.promise, value);
        };
        QueueItem.prototype.otherCallRejected = function(value) {
          unwrap(this.promise, this.onRejected, value);
        };
        function unwrap(promise, func, value) {
          immediate(function() {
            var returnValue;
            try {
              returnValue = func(value);
            } catch (e) {
              return handlers.reject(promise, e);
            }
            if (returnValue === promise) {
              handlers.reject(promise, new TypeError("Cannot resolve promise with itself"));
            } else {
              handlers.resolve(promise, returnValue);
            }
          });
        }
        handlers.resolve = function(self2, value) {
          var result = tryCatch(getThen, value);
          if (result.status === "error") {
            return handlers.reject(self2, result.value);
          }
          var thenable = result.value;
          if (thenable) {
            safelyResolveThenable(self2, thenable);
          } else {
            self2.state = FULFILLED;
            self2.outcome = value;
            var i = -1;
            var len = self2.queue.length;
            while (++i < len) {
              self2.queue[i].callFulfilled(value);
            }
          }
          return self2;
        };
        handlers.reject = function(self2, error) {
          self2.state = REJECTED;
          self2.outcome = error;
          var i = -1;
          var len = self2.queue.length;
          while (++i < len) {
            self2.queue[i].callRejected(error);
          }
          return self2;
        };
        function getThen(obj) {
          var then = obj && obj.then;
          if (obj && (typeof obj === "object" || typeof obj === "function") && typeof then === "function") {
            return function appyThen() {
              then.apply(obj, arguments);
            };
          }
        }
        function safelyResolveThenable(self2, thenable) {
          var called = false;
          function onError(value) {
            if (called) {
              return;
            }
            called = true;
            handlers.reject(self2, value);
          }
          function onSuccess(value) {
            if (called) {
              return;
            }
            called = true;
            handlers.resolve(self2, value);
          }
          function tryToUnwrap() {
            thenable(onSuccess, onError);
          }
          var result = tryCatch(tryToUnwrap);
          if (result.status === "error") {
            onError(result.value);
          }
        }
        function tryCatch(func, value) {
          var out = {};
          try {
            out.value = func(value);
            out.status = "success";
          } catch (e) {
            out.status = "error";
            out.value = e;
          }
          return out;
        }
        Promise2.resolve = resolve;
        function resolve(value) {
          if (value instanceof this) {
            return value;
          }
          return handlers.resolve(new this(INTERNAL), value);
        }
        Promise2.reject = reject;
        function reject(reason) {
          var promise = new this(INTERNAL);
          return handlers.reject(promise, reason);
        }
        Promise2.all = all;
        function all(iterable) {
          var self2 = this;
          if (Object.prototype.toString.call(iterable) !== "[object Array]") {
            return this.reject(new TypeError("must be an array"));
          }
          var len = iterable.length;
          var called = false;
          if (!len) {
            return this.resolve([]);
          }
          var values = new Array(len);
          var resolved = 0;
          var i = -1;
          var promise = new this(INTERNAL);
          while (++i < len) {
            allResolver(iterable[i], i);
          }
          return promise;
          function allResolver(value, i2) {
            self2.resolve(value).then(resolveFromAll, function(error) {
              if (!called) {
                called = true;
                handlers.reject(promise, error);
              }
            });
            function resolveFromAll(outValue) {
              values[i2] = outValue;
              if (++resolved === len && !called) {
                called = true;
                handlers.resolve(promise, values);
              }
            }
          }
        }
        Promise2.race = race;
        function race(iterable) {
          var self2 = this;
          if (Object.prototype.toString.call(iterable) !== "[object Array]") {
            return this.reject(new TypeError("must be an array"));
          }
          var len = iterable.length;
          var called = false;
          if (!len) {
            return this.resolve([]);
          }
          var i = -1;
          var promise = new this(INTERNAL);
          while (++i < len) {
            resolver(iterable[i]);
          }
          return promise;
          function resolver(value) {
            self2.resolve(value).then(function(response) {
              if (!called) {
                called = true;
                handlers.resolve(promise, response);
              }
            }, function(error) {
              if (!called) {
                called = true;
                handlers.reject(promise, error);
              }
            });
          }
        }
      }, { "1": 1 }], 3: [function(_dereq_, module3, exports3) {
        (function(global2) {
          "use strict";
          if (typeof global2.Promise !== "function") {
            global2.Promise = _dereq_(2);
          }
        }).call(this, typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {});
      }, { "2": 2 }], 4: [function(_dereq_, module3, exports3) {
        "use strict";
        var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function(obj) {
          return typeof obj;
        } : function(obj) {
          return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj;
        };
        function _classCallCheck(instance, Constructor) {
          if (!(instance instanceof Constructor)) {
            throw new TypeError("Cannot call a class as a function");
          }
        }
        function getIDB() {
          try {
            if (typeof indexedDB !== "undefined") {
              return indexedDB;
            }
            if (typeof webkitIndexedDB !== "undefined") {
              return webkitIndexedDB;
            }
            if (typeof mozIndexedDB !== "undefined") {
              return mozIndexedDB;
            }
            if (typeof OIndexedDB !== "undefined") {
              return OIndexedDB;
            }
            if (typeof msIndexedDB !== "undefined") {
              return msIndexedDB;
            }
          } catch (e) {
            return;
          }
        }
        var idb = getIDB();
        function isIndexedDBValid() {
          try {
            if (!idb || !idb.open) {
              return false;
            }
            var isSafari = typeof openDatabase !== "undefined" && /(Safari|iPhone|iPad|iPod)/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent) && !/BlackBerry/.test(navigator.platform);
            var hasFetch = typeof fetch === "function" && fetch.toString().indexOf("[native code") !== -1;
            return (!isSafari || hasFetch) && typeof indexedDB !== "undefined" && // some outdated implementations of IDB that appear on Samsung
            // and HTC Android devices <4.4 are missing IDBKeyRange
            // See: https://github.com/mozilla/localForage/issues/128
            // See: https://github.com/mozilla/localForage/issues/272
            typeof IDBKeyRange !== "undefined";
          } catch (e) {
            return false;
          }
        }
        function createBlob(parts, properties) {
          parts = parts || [];
          properties = properties || {};
          try {
            return new Blob(parts, properties);
          } catch (e) {
            if (e.name !== "TypeError") {
              throw e;
            }
            var Builder = typeof BlobBuilder !== "undefined" ? BlobBuilder : typeof MSBlobBuilder !== "undefined" ? MSBlobBuilder : typeof MozBlobBuilder !== "undefined" ? MozBlobBuilder : WebKitBlobBuilder;
            var builder = new Builder();
            for (var i = 0; i < parts.length; i += 1) {
              builder.append(parts[i]);
            }
            return builder.getBlob(properties.type);
          }
        }
        if (typeof Promise === "undefined") {
          _dereq_(3);
        }
        var Promise$1 = Promise;
        function executeCallback(promise, callback) {
          if (callback) {
            promise.then(function(result) {
              callback(null, result);
            }, function(error) {
              callback(error);
            });
          }
        }
        function executeTwoCallbacks(promise, callback, errorCallback) {
          if (typeof callback === "function") {
            promise.then(callback);
          }
          if (typeof errorCallback === "function") {
            promise["catch"](errorCallback);
          }
        }
        function normalizeKey(key2) {
          if (typeof key2 !== "string") {
            console.warn(key2 + " used as a key, but it is not a string.");
            key2 = String(key2);
          }
          return key2;
        }
        function getCallback() {
          if (arguments.length && typeof arguments[arguments.length - 1] === "function") {
            return arguments[arguments.length - 1];
          }
        }
        var DETECT_BLOB_SUPPORT_STORE = "local-forage-detect-blob-support";
        var supportsBlobs = void 0;
        var dbContexts = {};
        var toString = Object.prototype.toString;
        var READ_ONLY = "readonly";
        var READ_WRITE = "readwrite";
        function _binStringToArrayBuffer(bin) {
          var length2 = bin.length;
          var buf = new ArrayBuffer(length2);
          var arr = new Uint8Array(buf);
          for (var i = 0; i < length2; i++) {
            arr[i] = bin.charCodeAt(i);
          }
          return buf;
        }
        function _checkBlobSupportWithoutCaching(idb2) {
          return new Promise$1(function(resolve) {
            var txn = idb2.transaction(DETECT_BLOB_SUPPORT_STORE, READ_WRITE);
            var blob = createBlob([""]);
            txn.objectStore(DETECT_BLOB_SUPPORT_STORE).put(blob, "key");
            txn.onabort = function(e) {
              e.preventDefault();
              e.stopPropagation();
              resolve(false);
            };
            txn.oncomplete = function() {
              var matchedChrome = navigator.userAgent.match(/Chrome\/(\d+)/);
              var matchedEdge = navigator.userAgent.match(/Edge\//);
              resolve(matchedEdge || !matchedChrome || parseInt(matchedChrome[1], 10) >= 43);
            };
          })["catch"](function() {
            return false;
          });
        }
        function _checkBlobSupport(idb2) {
          if (typeof supportsBlobs === "boolean") {
            return Promise$1.resolve(supportsBlobs);
          }
          return _checkBlobSupportWithoutCaching(idb2).then(function(value) {
            supportsBlobs = value;
            return supportsBlobs;
          });
        }
        function _deferReadiness(dbInfo) {
          var dbContext = dbContexts[dbInfo.name];
          var deferredOperation = {};
          deferredOperation.promise = new Promise$1(function(resolve, reject) {
            deferredOperation.resolve = resolve;
            deferredOperation.reject = reject;
          });
          dbContext.deferredOperations.push(deferredOperation);
          if (!dbContext.dbReady) {
            dbContext.dbReady = deferredOperation.promise;
          } else {
            dbContext.dbReady = dbContext.dbReady.then(function() {
              return deferredOperation.promise;
            });
          }
        }
        function _advanceReadiness(dbInfo) {
          var dbContext = dbContexts[dbInfo.name];
          var deferredOperation = dbContext.deferredOperations.pop();
          if (deferredOperation) {
            deferredOperation.resolve();
            return deferredOperation.promise;
          }
        }
        function _rejectReadiness(dbInfo, err) {
          var dbContext = dbContexts[dbInfo.name];
          var deferredOperation = dbContext.deferredOperations.pop();
          if (deferredOperation) {
            deferredOperation.reject(err);
            return deferredOperation.promise;
          }
        }
        function _getConnection(dbInfo, upgradeNeeded) {
          return new Promise$1(function(resolve, reject) {
            dbContexts[dbInfo.name] = dbContexts[dbInfo.name] || createDbContext();
            if (dbInfo.db) {
              if (upgradeNeeded) {
                _deferReadiness(dbInfo);
                dbInfo.db.close();
              } else {
                return resolve(dbInfo.db);
              }
            }
            var dbArgs = [dbInfo.name];
            if (upgradeNeeded) {
              dbArgs.push(dbInfo.version);
            }
            var openreq = idb.open.apply(idb, dbArgs);
            if (upgradeNeeded) {
              openreq.onupgradeneeded = function(e) {
                var db = openreq.result;
                try {
                  db.createObjectStore(dbInfo.storeName);
                  if (e.oldVersion <= 1) {
                    db.createObjectStore(DETECT_BLOB_SUPPORT_STORE);
                  }
                } catch (ex) {
                  if (ex.name === "ConstraintError") {
                    console.warn('The database "' + dbInfo.name + '" has been upgraded from version ' + e.oldVersion + " to version " + e.newVersion + ', but the storage "' + dbInfo.storeName + '" already exists.');
                  } else {
                    throw ex;
                  }
                }
              };
            }
            openreq.onerror = function(e) {
              e.preventDefault();
              reject(openreq.error);
            };
            openreq.onsuccess = function() {
              var db = openreq.result;
              db.onversionchange = function(e) {
                e.target.close();
              };
              resolve(db);
              _advanceReadiness(dbInfo);
            };
          });
        }
        function _getOriginalConnection(dbInfo) {
          return _getConnection(dbInfo, false);
        }
        function _getUpgradedConnection(dbInfo) {
          return _getConnection(dbInfo, true);
        }
        function _isUpgradeNeeded(dbInfo, defaultVersion) {
          if (!dbInfo.db) {
            return true;
          }
          var isNewStore = !dbInfo.db.objectStoreNames.contains(dbInfo.storeName);
          var isDowngrade = dbInfo.version < dbInfo.db.version;
          var isUpgrade = dbInfo.version > dbInfo.db.version;
          if (isDowngrade) {
            if (dbInfo.version !== defaultVersion) {
              console.warn('The database "' + dbInfo.name + `" can't be downgraded from version ` + dbInfo.db.version + " to version " + dbInfo.version + ".");
            }
            dbInfo.version = dbInfo.db.version;
          }
          if (isUpgrade || isNewStore) {
            if (isNewStore) {
              var incVersion = dbInfo.db.version + 1;
              if (incVersion > dbInfo.version) {
                dbInfo.version = incVersion;
              }
            }
            return true;
          }
          return false;
        }
        function _encodeBlob(blob) {
          return new Promise$1(function(resolve, reject) {
            var reader = new FileReader();
            reader.onerror = reject;
            reader.onloadend = function(e) {
              var base64 = btoa(e.target.result || "");
              resolve({
                __local_forage_encoded_blob: true,
                data: base64,
                type: blob.type
              });
            };
            reader.readAsBinaryString(blob);
          });
        }
        function _decodeBlob(encodedBlob) {
          var arrayBuff = _binStringToArrayBuffer(atob(encodedBlob.data));
          return createBlob([arrayBuff], { type: encodedBlob.type });
        }
        function _isEncodedBlob(value) {
          return value && value.__local_forage_encoded_blob;
        }
        function _fullyReady(callback) {
          var self2 = this;
          var promise = self2._initReady().then(function() {
            var dbContext = dbContexts[self2._dbInfo.name];
            if (dbContext && dbContext.dbReady) {
              return dbContext.dbReady;
            }
          });
          executeTwoCallbacks(promise, callback, callback);
          return promise;
        }
        function _tryReconnect(dbInfo) {
          _deferReadiness(dbInfo);
          var dbContext = dbContexts[dbInfo.name];
          var forages = dbContext.forages;
          for (var i = 0; i < forages.length; i++) {
            var forage = forages[i];
            if (forage._dbInfo.db) {
              forage._dbInfo.db.close();
              forage._dbInfo.db = null;
            }
          }
          dbInfo.db = null;
          return _getOriginalConnection(dbInfo).then(function(db) {
            dbInfo.db = db;
            if (_isUpgradeNeeded(dbInfo)) {
              return _getUpgradedConnection(dbInfo);
            }
            return db;
          }).then(function(db) {
            dbInfo.db = dbContext.db = db;
            for (var i2 = 0; i2 < forages.length; i2++) {
              forages[i2]._dbInfo.db = db;
            }
          })["catch"](function(err) {
            _rejectReadiness(dbInfo, err);
            throw err;
          });
        }
        function createTransaction(dbInfo, mode, callback, retries) {
          if (retries === void 0) {
            retries = 1;
          }
          try {
            var tx = dbInfo.db.transaction(dbInfo.storeName, mode);
            callback(null, tx);
          } catch (err) {
            if (retries > 0 && (!dbInfo.db || err.name === "InvalidStateError" || err.name === "NotFoundError")) {
              return Promise$1.resolve().then(function() {
                if (!dbInfo.db || err.name === "NotFoundError" && !dbInfo.db.objectStoreNames.contains(dbInfo.storeName) && dbInfo.version <= dbInfo.db.version) {
                  if (dbInfo.db) {
                    dbInfo.version = dbInfo.db.version + 1;
                  }
                  return _getUpgradedConnection(dbInfo);
                }
              }).then(function() {
                return _tryReconnect(dbInfo).then(function() {
                  createTransaction(dbInfo, mode, callback, retries - 1);
                });
              })["catch"](callback);
            }
            callback(err);
          }
        }
        function createDbContext() {
          return {
            // Running localForages sharing a database.
            forages: [],
            // Shared database.
            db: null,
            // Database readiness (promise).
            dbReady: null,
            // Deferred operations on the database.
            deferredOperations: []
          };
        }
        function _initStorage(options) {
          var self2 = this;
          var dbInfo = {
            db: null
          };
          if (options) {
            for (var i in options) {
              dbInfo[i] = options[i];
            }
          }
          var dbContext = dbContexts[dbInfo.name];
          if (!dbContext) {
            dbContext = createDbContext();
            dbContexts[dbInfo.name] = dbContext;
          }
          dbContext.forages.push(self2);
          if (!self2._initReady) {
            self2._initReady = self2.ready;
            self2.ready = _fullyReady;
          }
          var initPromises = [];
          function ignoreErrors() {
            return Promise$1.resolve();
          }
          for (var j = 0; j < dbContext.forages.length; j++) {
            var forage = dbContext.forages[j];
            if (forage !== self2) {
              initPromises.push(forage._initReady()["catch"](ignoreErrors));
            }
          }
          var forages = dbContext.forages.slice(0);
          return Promise$1.all(initPromises).then(function() {
            dbInfo.db = dbContext.db;
            return _getOriginalConnection(dbInfo);
          }).then(function(db) {
            dbInfo.db = db;
            if (_isUpgradeNeeded(dbInfo, self2._defaultConfig.version)) {
              return _getUpgradedConnection(dbInfo);
            }
            return db;
          }).then(function(db) {
            dbInfo.db = dbContext.db = db;
            self2._dbInfo = dbInfo;
            for (var k = 0; k < forages.length; k++) {
              var forage2 = forages[k];
              if (forage2 !== self2) {
                forage2._dbInfo.db = dbInfo.db;
                forage2._dbInfo.version = dbInfo.version;
              }
            }
          });
        }
        function getItem(key2, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_ONLY, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var req = store.get(key2);
                  req.onsuccess = function() {
                    var value = req.result;
                    if (value === void 0) {
                      value = null;
                    }
                    if (_isEncodedBlob(value)) {
                      value = _decodeBlob(value);
                    }
                    resolve(value);
                  };
                  req.onerror = function() {
                    reject(req.error);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function iterate(iterator, callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_ONLY, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var req = store.openCursor();
                  var iterationNumber = 1;
                  req.onsuccess = function() {
                    var cursor = req.result;
                    if (cursor) {
                      var value = cursor.value;
                      if (_isEncodedBlob(value)) {
                        value = _decodeBlob(value);
                      }
                      var result = iterator(value, cursor.key, iterationNumber++);
                      if (result !== void 0) {
                        resolve(result);
                      } else {
                        cursor["continue"]();
                      }
                    } else {
                      resolve();
                    }
                  };
                  req.onerror = function() {
                    reject(req.error);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function setItem(key2, value, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = new Promise$1(function(resolve, reject) {
            var dbInfo;
            self2.ready().then(function() {
              dbInfo = self2._dbInfo;
              if (toString.call(value) === "[object Blob]") {
                return _checkBlobSupport(dbInfo.db).then(function(blobSupport) {
                  if (blobSupport) {
                    return value;
                  }
                  return _encodeBlob(value);
                });
              }
              return value;
            }).then(function(value2) {
              createTransaction(self2._dbInfo, READ_WRITE, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  if (value2 === null) {
                    value2 = void 0;
                  }
                  var req = store.put(value2, key2);
                  transaction.oncomplete = function() {
                    if (value2 === void 0) {
                      value2 = null;
                    }
                    resolve(value2);
                  };
                  transaction.onabort = transaction.onerror = function() {
                    var err2 = req.error ? req.error : req.transaction.error;
                    reject(err2);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function removeItem(key2, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_WRITE, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var req = store["delete"](key2);
                  transaction.oncomplete = function() {
                    resolve();
                  };
                  transaction.onerror = function() {
                    reject(req.error);
                  };
                  transaction.onabort = function() {
                    var err2 = req.error ? req.error : req.transaction.error;
                    reject(err2);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function clear(callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_WRITE, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var req = store.clear();
                  transaction.oncomplete = function() {
                    resolve();
                  };
                  transaction.onabort = transaction.onerror = function() {
                    var err2 = req.error ? req.error : req.transaction.error;
                    reject(err2);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function length(callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_ONLY, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var req = store.count();
                  req.onsuccess = function() {
                    resolve(req.result);
                  };
                  req.onerror = function() {
                    reject(req.error);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function key(n, callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            if (n < 0) {
              resolve(null);
              return;
            }
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_ONLY, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var advanced = false;
                  var req = store.openKeyCursor();
                  req.onsuccess = function() {
                    var cursor = req.result;
                    if (!cursor) {
                      resolve(null);
                      return;
                    }
                    if (n === 0) {
                      resolve(cursor.key);
                    } else {
                      if (!advanced) {
                        advanced = true;
                        cursor.advance(n);
                      } else {
                        resolve(cursor.key);
                      }
                    }
                  };
                  req.onerror = function() {
                    reject(req.error);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function keys(callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              createTransaction(self2._dbInfo, READ_ONLY, function(err, transaction) {
                if (err) {
                  return reject(err);
                }
                try {
                  var store = transaction.objectStore(self2._dbInfo.storeName);
                  var req = store.openKeyCursor();
                  var keys2 = [];
                  req.onsuccess = function() {
                    var cursor = req.result;
                    if (!cursor) {
                      resolve(keys2);
                      return;
                    }
                    keys2.push(cursor.key);
                    cursor["continue"]();
                  };
                  req.onerror = function() {
                    reject(req.error);
                  };
                } catch (e) {
                  reject(e);
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function dropInstance(options, callback) {
          callback = getCallback.apply(this, arguments);
          var currentConfig = this.config();
          options = typeof options !== "function" && options || {};
          if (!options.name) {
            options.name = options.name || currentConfig.name;
            options.storeName = options.storeName || currentConfig.storeName;
          }
          var self2 = this;
          var promise;
          if (!options.name) {
            promise = Promise$1.reject("Invalid arguments");
          } else {
            var isCurrentDb = options.name === currentConfig.name && self2._dbInfo.db;
            var dbPromise = isCurrentDb ? Promise$1.resolve(self2._dbInfo.db) : _getOriginalConnection(options).then(function(db) {
              var dbContext = dbContexts[options.name];
              var forages = dbContext.forages;
              dbContext.db = db;
              for (var i = 0; i < forages.length; i++) {
                forages[i]._dbInfo.db = db;
              }
              return db;
            });
            if (!options.storeName) {
              promise = dbPromise.then(function(db) {
                _deferReadiness(options);
                var dbContext = dbContexts[options.name];
                var forages = dbContext.forages;
                db.close();
                for (var i = 0; i < forages.length; i++) {
                  var forage = forages[i];
                  forage._dbInfo.db = null;
                }
                var dropDBPromise = new Promise$1(function(resolve, reject) {
                  var req = idb.deleteDatabase(options.name);
                  req.onerror = function() {
                    var db2 = req.result;
                    if (db2) {
                      db2.close();
                    }
                    reject(req.error);
                  };
                  req.onblocked = function() {
                    console.warn('dropInstance blocked for database "' + options.name + '" until all open connections are closed');
                  };
                  req.onsuccess = function() {
                    var db2 = req.result;
                    if (db2) {
                      db2.close();
                    }
                    resolve(db2);
                  };
                });
                return dropDBPromise.then(function(db2) {
                  dbContext.db = db2;
                  for (var i2 = 0; i2 < forages.length; i2++) {
                    var _forage = forages[i2];
                    _advanceReadiness(_forage._dbInfo);
                  }
                })["catch"](function(err) {
                  (_rejectReadiness(options, err) || Promise$1.resolve())["catch"](function() {
                  });
                  throw err;
                });
              });
            } else {
              promise = dbPromise.then(function(db) {
                if (!db.objectStoreNames.contains(options.storeName)) {
                  return;
                }
                var newVersion = db.version + 1;
                _deferReadiness(options);
                var dbContext = dbContexts[options.name];
                var forages = dbContext.forages;
                db.close();
                for (var i = 0; i < forages.length; i++) {
                  var forage = forages[i];
                  forage._dbInfo.db = null;
                  forage._dbInfo.version = newVersion;
                }
                var dropObjectPromise = new Promise$1(function(resolve, reject) {
                  var req = idb.open(options.name, newVersion);
                  req.onerror = function(err) {
                    var db2 = req.result;
                    db2.close();
                    reject(err);
                  };
                  req.onupgradeneeded = function() {
                    var db2 = req.result;
                    db2.deleteObjectStore(options.storeName);
                  };
                  req.onsuccess = function() {
                    var db2 = req.result;
                    db2.close();
                    resolve(db2);
                  };
                });
                return dropObjectPromise.then(function(db2) {
                  dbContext.db = db2;
                  for (var j = 0; j < forages.length; j++) {
                    var _forage2 = forages[j];
                    _forage2._dbInfo.db = db2;
                    _advanceReadiness(_forage2._dbInfo);
                  }
                })["catch"](function(err) {
                  (_rejectReadiness(options, err) || Promise$1.resolve())["catch"](function() {
                  });
                  throw err;
                });
              });
            }
          }
          executeCallback(promise, callback);
          return promise;
        }
        var asyncStorage = {
          _driver: "asyncStorage",
          _initStorage,
          _support: isIndexedDBValid(),
          iterate,
          getItem,
          setItem,
          removeItem,
          clear,
          length,
          key,
          keys,
          dropInstance
        };
        function isWebSQLValid() {
          return typeof openDatabase === "function";
        }
        var BASE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        var BLOB_TYPE_PREFIX = "~~local_forage_type~";
        var BLOB_TYPE_PREFIX_REGEX = /^~~local_forage_type~([^~]+)~/;
        var SERIALIZED_MARKER = "__lfsc__:";
        var SERIALIZED_MARKER_LENGTH = SERIALIZED_MARKER.length;
        var TYPE_ARRAYBUFFER = "arbf";
        var TYPE_BLOB = "blob";
        var TYPE_INT8ARRAY = "si08";
        var TYPE_UINT8ARRAY = "ui08";
        var TYPE_UINT8CLAMPEDARRAY = "uic8";
        var TYPE_INT16ARRAY = "si16";
        var TYPE_INT32ARRAY = "si32";
        var TYPE_UINT16ARRAY = "ur16";
        var TYPE_UINT32ARRAY = "ui32";
        var TYPE_FLOAT32ARRAY = "fl32";
        var TYPE_FLOAT64ARRAY = "fl64";
        var TYPE_SERIALIZED_MARKER_LENGTH = SERIALIZED_MARKER_LENGTH + TYPE_ARRAYBUFFER.length;
        var toString$1 = Object.prototype.toString;
        function stringToBuffer(serializedString) {
          var bufferLength = serializedString.length * 0.75;
          var len = serializedString.length;
          var i;
          var p = 0;
          var encoded1, encoded2, encoded3, encoded4;
          if (serializedString[serializedString.length - 1] === "=") {
            bufferLength--;
            if (serializedString[serializedString.length - 2] === "=") {
              bufferLength--;
            }
          }
          var buffer = new ArrayBuffer(bufferLength);
          var bytes = new Uint8Array(buffer);
          for (i = 0; i < len; i += 4) {
            encoded1 = BASE_CHARS.indexOf(serializedString[i]);
            encoded2 = BASE_CHARS.indexOf(serializedString[i + 1]);
            encoded3 = BASE_CHARS.indexOf(serializedString[i + 2]);
            encoded4 = BASE_CHARS.indexOf(serializedString[i + 3]);
            bytes[p++] = encoded1 << 2 | encoded2 >> 4;
            bytes[p++] = (encoded2 & 15) << 4 | encoded3 >> 2;
            bytes[p++] = (encoded3 & 3) << 6 | encoded4 & 63;
          }
          return buffer;
        }
        function bufferToString(buffer) {
          var bytes = new Uint8Array(buffer);
          var base64String = "";
          var i;
          for (i = 0; i < bytes.length; i += 3) {
            base64String += BASE_CHARS[bytes[i] >> 2];
            base64String += BASE_CHARS[(bytes[i] & 3) << 4 | bytes[i + 1] >> 4];
            base64String += BASE_CHARS[(bytes[i + 1] & 15) << 2 | bytes[i + 2] >> 6];
            base64String += BASE_CHARS[bytes[i + 2] & 63];
          }
          if (bytes.length % 3 === 2) {
            base64String = base64String.substring(0, base64String.length - 1) + "=";
          } else if (bytes.length % 3 === 1) {
            base64String = base64String.substring(0, base64String.length - 2) + "==";
          }
          return base64String;
        }
        function serialize(value, callback) {
          var valueType = "";
          if (value) {
            valueType = toString$1.call(value);
          }
          if (value && (valueType === "[object ArrayBuffer]" || value.buffer && toString$1.call(value.buffer) === "[object ArrayBuffer]")) {
            var buffer;
            var marker = SERIALIZED_MARKER;
            if (value instanceof ArrayBuffer) {
              buffer = value;
              marker += TYPE_ARRAYBUFFER;
            } else {
              buffer = value.buffer;
              if (valueType === "[object Int8Array]") {
                marker += TYPE_INT8ARRAY;
              } else if (valueType === "[object Uint8Array]") {
                marker += TYPE_UINT8ARRAY;
              } else if (valueType === "[object Uint8ClampedArray]") {
                marker += TYPE_UINT8CLAMPEDARRAY;
              } else if (valueType === "[object Int16Array]") {
                marker += TYPE_INT16ARRAY;
              } else if (valueType === "[object Uint16Array]") {
                marker += TYPE_UINT16ARRAY;
              } else if (valueType === "[object Int32Array]") {
                marker += TYPE_INT32ARRAY;
              } else if (valueType === "[object Uint32Array]") {
                marker += TYPE_UINT32ARRAY;
              } else if (valueType === "[object Float32Array]") {
                marker += TYPE_FLOAT32ARRAY;
              } else if (valueType === "[object Float64Array]") {
                marker += TYPE_FLOAT64ARRAY;
              } else {
                callback(new Error("Failed to get type for BinaryArray"));
              }
            }
            callback(marker + bufferToString(buffer));
          } else if (valueType === "[object Blob]") {
            var fileReader = new FileReader();
            fileReader.onload = function() {
              var str = BLOB_TYPE_PREFIX + value.type + "~" + bufferToString(this.result);
              callback(SERIALIZED_MARKER + TYPE_BLOB + str);
            };
            fileReader.readAsArrayBuffer(value);
          } else {
            try {
              callback(JSON.stringify(value));
            } catch (e) {
              console.error("Couldn't convert value into a JSON string: ", value);
              callback(null, e);
            }
          }
        }
        function deserialize(value) {
          if (value.substring(0, SERIALIZED_MARKER_LENGTH) !== SERIALIZED_MARKER) {
            return JSON.parse(value);
          }
          var serializedString = value.substring(TYPE_SERIALIZED_MARKER_LENGTH);
          var type = value.substring(SERIALIZED_MARKER_LENGTH, TYPE_SERIALIZED_MARKER_LENGTH);
          var blobType;
          if (type === TYPE_BLOB && BLOB_TYPE_PREFIX_REGEX.test(serializedString)) {
            var matcher = serializedString.match(BLOB_TYPE_PREFIX_REGEX);
            blobType = matcher[1];
            serializedString = serializedString.substring(matcher[0].length);
          }
          var buffer = stringToBuffer(serializedString);
          switch (type) {
            case TYPE_ARRAYBUFFER:
              return buffer;
            case TYPE_BLOB:
              return createBlob([buffer], { type: blobType });
            case TYPE_INT8ARRAY:
              return new Int8Array(buffer);
            case TYPE_UINT8ARRAY:
              return new Uint8Array(buffer);
            case TYPE_UINT8CLAMPEDARRAY:
              return new Uint8ClampedArray(buffer);
            case TYPE_INT16ARRAY:
              return new Int16Array(buffer);
            case TYPE_UINT16ARRAY:
              return new Uint16Array(buffer);
            case TYPE_INT32ARRAY:
              return new Int32Array(buffer);
            case TYPE_UINT32ARRAY:
              return new Uint32Array(buffer);
            case TYPE_FLOAT32ARRAY:
              return new Float32Array(buffer);
            case TYPE_FLOAT64ARRAY:
              return new Float64Array(buffer);
            default:
              throw new Error("Unkown type: " + type);
          }
        }
        var localforageSerializer = {
          serialize,
          deserialize,
          stringToBuffer,
          bufferToString
        };
        function createDbTable(t, dbInfo, callback, errorCallback) {
          t.executeSql("CREATE TABLE IF NOT EXISTS " + dbInfo.storeName + " (id INTEGER PRIMARY KEY, key unique, value)", [], callback, errorCallback);
        }
        function _initStorage$1(options) {
          var self2 = this;
          var dbInfo = {
            db: null
          };
          if (options) {
            for (var i in options) {
              dbInfo[i] = typeof options[i] !== "string" ? options[i].toString() : options[i];
            }
          }
          var dbInfoPromise = new Promise$1(function(resolve, reject) {
            try {
              dbInfo.db = openDatabase(dbInfo.name, String(dbInfo.version), dbInfo.description, dbInfo.size);
            } catch (e) {
              return reject(e);
            }
            dbInfo.db.transaction(function(t) {
              createDbTable(t, dbInfo, function() {
                self2._dbInfo = dbInfo;
                resolve();
              }, function(t2, error) {
                reject(error);
              });
            }, reject);
          });
          dbInfo.serializer = localforageSerializer;
          return dbInfoPromise;
        }
        function tryExecuteSql(t, dbInfo, sqlStatement, args, callback, errorCallback) {
          t.executeSql(sqlStatement, args, callback, function(t2, error) {
            if (error.code === error.SYNTAX_ERR) {
              t2.executeSql("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", [dbInfo.storeName], function(t3, results) {
                if (!results.rows.length) {
                  createDbTable(t3, dbInfo, function() {
                    t3.executeSql(sqlStatement, args, callback, errorCallback);
                  }, errorCallback);
                } else {
                  errorCallback(t3, error);
                }
              }, errorCallback);
            } else {
              errorCallback(t2, error);
            }
          }, errorCallback);
        }
        function getItem$1(key2, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "SELECT * FROM " + dbInfo.storeName + " WHERE key = ? LIMIT 1", [key2], function(t2, results) {
                  var result = results.rows.length ? results.rows.item(0).value : null;
                  if (result) {
                    result = dbInfo.serializer.deserialize(result);
                  }
                  resolve(result);
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function iterate$1(iterator, callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "SELECT * FROM " + dbInfo.storeName, [], function(t2, results) {
                  var rows = results.rows;
                  var length2 = rows.length;
                  for (var i = 0; i < length2; i++) {
                    var item = rows.item(i);
                    var result = item.value;
                    if (result) {
                      result = dbInfo.serializer.deserialize(result);
                    }
                    result = iterator(result, item.key, i + 1);
                    if (result !== void 0) {
                      resolve(result);
                      return;
                    }
                  }
                  resolve();
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function _setItem(key2, value, callback, retriesLeft) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              if (value === void 0) {
                value = null;
              }
              var originalValue = value;
              var dbInfo = self2._dbInfo;
              dbInfo.serializer.serialize(value, function(value2, error) {
                if (error) {
                  reject(error);
                } else {
                  dbInfo.db.transaction(function(t) {
                    tryExecuteSql(t, dbInfo, "INSERT OR REPLACE INTO " + dbInfo.storeName + " (key, value) VALUES (?, ?)", [key2, value2], function() {
                      resolve(originalValue);
                    }, function(t2, error2) {
                      reject(error2);
                    });
                  }, function(sqlError) {
                    if (sqlError.code === sqlError.QUOTA_ERR) {
                      if (retriesLeft > 0) {
                        resolve(_setItem.apply(self2, [key2, originalValue, callback, retriesLeft - 1]));
                        return;
                      }
                      reject(sqlError);
                    }
                  });
                }
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function setItem$1(key2, value, callback) {
          return _setItem.apply(this, [key2, value, callback, 1]);
        }
        function removeItem$1(key2, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "DELETE FROM " + dbInfo.storeName + " WHERE key = ?", [key2], function() {
                  resolve();
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function clear$1(callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "DELETE FROM " + dbInfo.storeName, [], function() {
                  resolve();
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function length$1(callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "SELECT COUNT(key) as c FROM " + dbInfo.storeName, [], function(t2, results) {
                  var result = results.rows.item(0).c;
                  resolve(result);
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function key$1(n, callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "SELECT key FROM " + dbInfo.storeName + " WHERE id = ? LIMIT 1", [n + 1], function(t2, results) {
                  var result = results.rows.length ? results.rows.item(0).key : null;
                  resolve(result);
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function keys$1(callback) {
          var self2 = this;
          var promise = new Promise$1(function(resolve, reject) {
            self2.ready().then(function() {
              var dbInfo = self2._dbInfo;
              dbInfo.db.transaction(function(t) {
                tryExecuteSql(t, dbInfo, "SELECT key FROM " + dbInfo.storeName, [], function(t2, results) {
                  var keys2 = [];
                  for (var i = 0; i < results.rows.length; i++) {
                    keys2.push(results.rows.item(i).key);
                  }
                  resolve(keys2);
                }, function(t2, error) {
                  reject(error);
                });
              });
            })["catch"](reject);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function getAllStoreNames(db) {
          return new Promise$1(function(resolve, reject) {
            db.transaction(function(t) {
              t.executeSql("SELECT name FROM sqlite_master WHERE type='table' AND name <> '__WebKitDatabaseInfoTable__'", [], function(t2, results) {
                var storeNames = [];
                for (var i = 0; i < results.rows.length; i++) {
                  storeNames.push(results.rows.item(i).name);
                }
                resolve({
                  db,
                  storeNames
                });
              }, function(t2, error) {
                reject(error);
              });
            }, function(sqlError) {
              reject(sqlError);
            });
          });
        }
        function dropInstance$1(options, callback) {
          callback = getCallback.apply(this, arguments);
          var currentConfig = this.config();
          options = typeof options !== "function" && options || {};
          if (!options.name) {
            options.name = options.name || currentConfig.name;
            options.storeName = options.storeName || currentConfig.storeName;
          }
          var self2 = this;
          var promise;
          if (!options.name) {
            promise = Promise$1.reject("Invalid arguments");
          } else {
            promise = new Promise$1(function(resolve) {
              var db;
              if (options.name === currentConfig.name) {
                db = self2._dbInfo.db;
              } else {
                db = openDatabase(options.name, "", "", 0);
              }
              if (!options.storeName) {
                resolve(getAllStoreNames(db));
              } else {
                resolve({
                  db,
                  storeNames: [options.storeName]
                });
              }
            }).then(function(operationInfo) {
              return new Promise$1(function(resolve, reject) {
                operationInfo.db.transaction(function(t) {
                  function dropTable(storeName) {
                    return new Promise$1(function(resolve2, reject2) {
                      t.executeSql("DROP TABLE IF EXISTS " + storeName, [], function() {
                        resolve2();
                      }, function(t2, error) {
                        reject2(error);
                      });
                    });
                  }
                  var operations = [];
                  for (var i = 0, len = operationInfo.storeNames.length; i < len; i++) {
                    operations.push(dropTable(operationInfo.storeNames[i]));
                  }
                  Promise$1.all(operations).then(function() {
                    resolve();
                  })["catch"](function(e) {
                    reject(e);
                  });
                }, function(sqlError) {
                  reject(sqlError);
                });
              });
            });
          }
          executeCallback(promise, callback);
          return promise;
        }
        var webSQLStorage = {
          _driver: "webSQLStorage",
          _initStorage: _initStorage$1,
          _support: isWebSQLValid(),
          iterate: iterate$1,
          getItem: getItem$1,
          setItem: setItem$1,
          removeItem: removeItem$1,
          clear: clear$1,
          length: length$1,
          key: key$1,
          keys: keys$1,
          dropInstance: dropInstance$1
        };
        function isLocalStorageValid() {
          try {
            return typeof localStorage !== "undefined" && "setItem" in localStorage && // in IE8 typeof localStorage.setItem === 'object'
            !!localStorage.setItem;
          } catch (e) {
            return false;
          }
        }
        function _getKeyPrefix(options, defaultConfig) {
          var keyPrefix = options.name + "/";
          if (options.storeName !== defaultConfig.storeName) {
            keyPrefix += options.storeName + "/";
          }
          return keyPrefix;
        }
        function checkIfLocalStorageThrows() {
          var localStorageTestKey = "_localforage_support_test";
          try {
            localStorage.setItem(localStorageTestKey, true);
            localStorage.removeItem(localStorageTestKey);
            return false;
          } catch (e) {
            return true;
          }
        }
        function _isLocalStorageUsable() {
          return !checkIfLocalStorageThrows() || localStorage.length > 0;
        }
        function _initStorage$2(options) {
          var self2 = this;
          var dbInfo = {};
          if (options) {
            for (var i in options) {
              dbInfo[i] = options[i];
            }
          }
          dbInfo.keyPrefix = _getKeyPrefix(options, self2._defaultConfig);
          if (!_isLocalStorageUsable()) {
            return Promise$1.reject();
          }
          self2._dbInfo = dbInfo;
          dbInfo.serializer = localforageSerializer;
          return Promise$1.resolve();
        }
        function clear$2(callback) {
          var self2 = this;
          var promise = self2.ready().then(function() {
            var keyPrefix = self2._dbInfo.keyPrefix;
            for (var i = localStorage.length - 1; i >= 0; i--) {
              var key2 = localStorage.key(i);
              if (key2.indexOf(keyPrefix) === 0) {
                localStorage.removeItem(key2);
              }
            }
          });
          executeCallback(promise, callback);
          return promise;
        }
        function getItem$2(key2, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = self2.ready().then(function() {
            var dbInfo = self2._dbInfo;
            var result = localStorage.getItem(dbInfo.keyPrefix + key2);
            if (result) {
              result = dbInfo.serializer.deserialize(result);
            }
            return result;
          });
          executeCallback(promise, callback);
          return promise;
        }
        function iterate$2(iterator, callback) {
          var self2 = this;
          var promise = self2.ready().then(function() {
            var dbInfo = self2._dbInfo;
            var keyPrefix = dbInfo.keyPrefix;
            var keyPrefixLength = keyPrefix.length;
            var length2 = localStorage.length;
            var iterationNumber = 1;
            for (var i = 0; i < length2; i++) {
              var key2 = localStorage.key(i);
              if (key2.indexOf(keyPrefix) !== 0) {
                continue;
              }
              var value = localStorage.getItem(key2);
              if (value) {
                value = dbInfo.serializer.deserialize(value);
              }
              value = iterator(value, key2.substring(keyPrefixLength), iterationNumber++);
              if (value !== void 0) {
                return value;
              }
            }
          });
          executeCallback(promise, callback);
          return promise;
        }
        function key$2(n, callback) {
          var self2 = this;
          var promise = self2.ready().then(function() {
            var dbInfo = self2._dbInfo;
            var result;
            try {
              result = localStorage.key(n);
            } catch (error) {
              result = null;
            }
            if (result) {
              result = result.substring(dbInfo.keyPrefix.length);
            }
            return result;
          });
          executeCallback(promise, callback);
          return promise;
        }
        function keys$2(callback) {
          var self2 = this;
          var promise = self2.ready().then(function() {
            var dbInfo = self2._dbInfo;
            var length2 = localStorage.length;
            var keys2 = [];
            for (var i = 0; i < length2; i++) {
              var itemKey = localStorage.key(i);
              if (itemKey.indexOf(dbInfo.keyPrefix) === 0) {
                keys2.push(itemKey.substring(dbInfo.keyPrefix.length));
              }
            }
            return keys2;
          });
          executeCallback(promise, callback);
          return promise;
        }
        function length$2(callback) {
          var self2 = this;
          var promise = self2.keys().then(function(keys2) {
            return keys2.length;
          });
          executeCallback(promise, callback);
          return promise;
        }
        function removeItem$2(key2, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = self2.ready().then(function() {
            var dbInfo = self2._dbInfo;
            localStorage.removeItem(dbInfo.keyPrefix + key2);
          });
          executeCallback(promise, callback);
          return promise;
        }
        function setItem$2(key2, value, callback) {
          var self2 = this;
          key2 = normalizeKey(key2);
          var promise = self2.ready().then(function() {
            if (value === void 0) {
              value = null;
            }
            var originalValue = value;
            return new Promise$1(function(resolve, reject) {
              var dbInfo = self2._dbInfo;
              dbInfo.serializer.serialize(value, function(value2, error) {
                if (error) {
                  reject(error);
                } else {
                  try {
                    localStorage.setItem(dbInfo.keyPrefix + key2, value2);
                    resolve(originalValue);
                  } catch (e) {
                    if (e.name === "QuotaExceededError" || e.name === "NS_ERROR_DOM_QUOTA_REACHED") {
                      reject(e);
                    }
                    reject(e);
                  }
                }
              });
            });
          });
          executeCallback(promise, callback);
          return promise;
        }
        function dropInstance$2(options, callback) {
          callback = getCallback.apply(this, arguments);
          options = typeof options !== "function" && options || {};
          if (!options.name) {
            var currentConfig = this.config();
            options.name = options.name || currentConfig.name;
            options.storeName = options.storeName || currentConfig.storeName;
          }
          var self2 = this;
          var promise;
          if (!options.name) {
            promise = Promise$1.reject("Invalid arguments");
          } else {
            promise = new Promise$1(function(resolve) {
              if (!options.storeName) {
                resolve(options.name + "/");
              } else {
                resolve(_getKeyPrefix(options, self2._defaultConfig));
              }
            }).then(function(keyPrefix) {
              for (var i = localStorage.length - 1; i >= 0; i--) {
                var key2 = localStorage.key(i);
                if (key2.indexOf(keyPrefix) === 0) {
                  localStorage.removeItem(key2);
                }
              }
            });
          }
          executeCallback(promise, callback);
          return promise;
        }
        var localStorageWrapper = {
          _driver: "localStorageWrapper",
          _initStorage: _initStorage$2,
          _support: isLocalStorageValid(),
          iterate: iterate$2,
          getItem: getItem$2,
          setItem: setItem$2,
          removeItem: removeItem$2,
          clear: clear$2,
          length: length$2,
          key: key$2,
          keys: keys$2,
          dropInstance: dropInstance$2
        };
        var sameValue = function sameValue2(x, y) {
          return x === y || typeof x === "number" && typeof y === "number" && isNaN(x) && isNaN(y);
        };
        var includes = function includes2(array, searchElement) {
          var len = array.length;
          var i = 0;
          while (i < len) {
            if (sameValue(array[i], searchElement)) {
              return true;
            }
            i++;
          }
          return false;
        };
        var isArray = Array.isArray || function(arg) {
          return Object.prototype.toString.call(arg) === "[object Array]";
        };
        var DefinedDrivers = {};
        var DriverSupport = {};
        var DefaultDrivers = {
          INDEXEDDB: asyncStorage,
          WEBSQL: webSQLStorage,
          LOCALSTORAGE: localStorageWrapper
        };
        var DefaultDriverOrder = [DefaultDrivers.INDEXEDDB._driver, DefaultDrivers.WEBSQL._driver, DefaultDrivers.LOCALSTORAGE._driver];
        var OptionalDriverMethods = ["dropInstance"];
        var LibraryMethods = ["clear", "getItem", "iterate", "key", "keys", "length", "removeItem", "setItem"].concat(OptionalDriverMethods);
        var DefaultConfig = {
          description: "",
          driver: DefaultDriverOrder.slice(),
          name: "localforage",
          // Default DB size is _JUST UNDER_ 5MB, as it's the highest size
          // we can use without a prompt.
          size: 4980736,
          storeName: "keyvaluepairs",
          version: 1
        };
        function callWhenReady(localForageInstance, libraryMethod) {
          localForageInstance[libraryMethod] = function() {
            var _args = arguments;
            return localForageInstance.ready().then(function() {
              return localForageInstance[libraryMethod].apply(localForageInstance, _args);
            });
          };
        }
        function extend() {
          for (var i = 1; i < arguments.length; i++) {
            var arg = arguments[i];
            if (arg) {
              for (var _key in arg) {
                if (arg.hasOwnProperty(_key)) {
                  if (isArray(arg[_key])) {
                    arguments[0][_key] = arg[_key].slice();
                  } else {
                    arguments[0][_key] = arg[_key];
                  }
                }
              }
            }
          }
          return arguments[0];
        }
        var LocalForage = function() {
          function LocalForage2(options) {
            _classCallCheck(this, LocalForage2);
            for (var driverTypeKey in DefaultDrivers) {
              if (DefaultDrivers.hasOwnProperty(driverTypeKey)) {
                var driver = DefaultDrivers[driverTypeKey];
                var driverName = driver._driver;
                this[driverTypeKey] = driverName;
                if (!DefinedDrivers[driverName]) {
                  this.defineDriver(driver);
                }
              }
            }
            this._defaultConfig = extend({}, DefaultConfig);
            this._config = extend({}, this._defaultConfig, options);
            this._driverSet = null;
            this._initDriver = null;
            this._ready = false;
            this._dbInfo = null;
            this._wrapLibraryMethodsWithReady();
            this.setDriver(this._config.driver)["catch"](function() {
            });
          }
          LocalForage2.prototype.config = function config(options) {
            if ((typeof options === "undefined" ? "undefined" : _typeof(options)) === "object") {
              if (this._ready) {
                return new Error("Can't call config() after localforage has been used.");
              }
              for (var i in options) {
                if (i === "storeName") {
                  options[i] = options[i].replace(/\W/g, "_");
                }
                if (i === "version" && typeof options[i] !== "number") {
                  return new Error("Database version must be a number.");
                }
                this._config[i] = options[i];
              }
              if ("driver" in options && options.driver) {
                return this.setDriver(this._config.driver);
              }
              return true;
            } else if (typeof options === "string") {
              return this._config[options];
            } else {
              return this._config;
            }
          };
          LocalForage2.prototype.defineDriver = function defineDriver(driverObject, callback, errorCallback) {
            var promise = new Promise$1(function(resolve, reject) {
              try {
                var driverName = driverObject._driver;
                var complianceError = new Error("Custom driver not compliant; see https://mozilla.github.io/localForage/#definedriver");
                if (!driverObject._driver) {
                  reject(complianceError);
                  return;
                }
                var driverMethods = LibraryMethods.concat("_initStorage");
                for (var i = 0, len = driverMethods.length; i < len; i++) {
                  var driverMethodName = driverMethods[i];
                  var isRequired = !includes(OptionalDriverMethods, driverMethodName);
                  if ((isRequired || driverObject[driverMethodName]) && typeof driverObject[driverMethodName] !== "function") {
                    reject(complianceError);
                    return;
                  }
                }
                var configureMissingMethods = function configureMissingMethods2() {
                  var methodNotImplementedFactory = function methodNotImplementedFactory2(methodName) {
                    return function() {
                      var error = new Error("Method " + methodName + " is not implemented by the current driver");
                      var promise2 = Promise$1.reject(error);
                      executeCallback(promise2, arguments[arguments.length - 1]);
                      return promise2;
                    };
                  };
                  for (var _i = 0, _len = OptionalDriverMethods.length; _i < _len; _i++) {
                    var optionalDriverMethod = OptionalDriverMethods[_i];
                    if (!driverObject[optionalDriverMethod]) {
                      driverObject[optionalDriverMethod] = methodNotImplementedFactory(optionalDriverMethod);
                    }
                  }
                };
                configureMissingMethods();
                var setDriverSupport = function setDriverSupport2(support) {
                  if (DefinedDrivers[driverName]) {
                    console.info("Redefining LocalForage driver: " + driverName);
                  }
                  DefinedDrivers[driverName] = driverObject;
                  DriverSupport[driverName] = support;
                  resolve();
                };
                if ("_support" in driverObject) {
                  if (driverObject._support && typeof driverObject._support === "function") {
                    driverObject._support().then(setDriverSupport, reject);
                  } else {
                    setDriverSupport(!!driverObject._support);
                  }
                } else {
                  setDriverSupport(true);
                }
              } catch (e) {
                reject(e);
              }
            });
            executeTwoCallbacks(promise, callback, errorCallback);
            return promise;
          };
          LocalForage2.prototype.driver = function driver() {
            return this._driver || null;
          };
          LocalForage2.prototype.getDriver = function getDriver(driverName, callback, errorCallback) {
            var getDriverPromise = DefinedDrivers[driverName] ? Promise$1.resolve(DefinedDrivers[driverName]) : Promise$1.reject(new Error("Driver not found."));
            executeTwoCallbacks(getDriverPromise, callback, errorCallback);
            return getDriverPromise;
          };
          LocalForage2.prototype.getSerializer = function getSerializer(callback) {
            var serializerPromise = Promise$1.resolve(localforageSerializer);
            executeTwoCallbacks(serializerPromise, callback);
            return serializerPromise;
          };
          LocalForage2.prototype.ready = function ready(callback) {
            var self2 = this;
            var promise = self2._driverSet.then(function() {
              if (self2._ready === null) {
                self2._ready = self2._initDriver();
              }
              return self2._ready;
            });
            executeTwoCallbacks(promise, callback, callback);
            return promise;
          };
          LocalForage2.prototype.setDriver = function setDriver(drivers, callback, errorCallback) {
            var self2 = this;
            if (!isArray(drivers)) {
              drivers = [drivers];
            }
            var supportedDrivers = this._getSupportedDrivers(drivers);
            function setDriverToConfig() {
              self2._config.driver = self2.driver();
            }
            function extendSelfWithDriver(driver) {
              self2._extend(driver);
              setDriverToConfig();
              self2._ready = self2._initStorage(self2._config);
              return self2._ready;
            }
            function initDriver(supportedDrivers2) {
              return function() {
                var currentDriverIndex = 0;
                function driverPromiseLoop() {
                  while (currentDriverIndex < supportedDrivers2.length) {
                    var driverName = supportedDrivers2[currentDriverIndex];
                    currentDriverIndex++;
                    self2._dbInfo = null;
                    self2._ready = null;
                    return self2.getDriver(driverName).then(extendSelfWithDriver)["catch"](driverPromiseLoop);
                  }
                  setDriverToConfig();
                  var error = new Error("No available storage method found.");
                  self2._driverSet = Promise$1.reject(error);
                  return self2._driverSet;
                }
                return driverPromiseLoop();
              };
            }
            var oldDriverSetDone = this._driverSet !== null ? this._driverSet["catch"](function() {
              return Promise$1.resolve();
            }) : Promise$1.resolve();
            this._driverSet = oldDriverSetDone.then(function() {
              var driverName = supportedDrivers[0];
              self2._dbInfo = null;
              self2._ready = null;
              return self2.getDriver(driverName).then(function(driver) {
                self2._driver = driver._driver;
                setDriverToConfig();
                self2._wrapLibraryMethodsWithReady();
                self2._initDriver = initDriver(supportedDrivers);
              });
            })["catch"](function() {
              setDriverToConfig();
              var error = new Error("No available storage method found.");
              self2._driverSet = Promise$1.reject(error);
              return self2._driverSet;
            });
            executeTwoCallbacks(this._driverSet, callback, errorCallback);
            return this._driverSet;
          };
          LocalForage2.prototype.supports = function supports(driverName) {
            return !!DriverSupport[driverName];
          };
          LocalForage2.prototype._extend = function _extend(libraryMethodsAndProperties) {
            extend(this, libraryMethodsAndProperties);
          };
          LocalForage2.prototype._getSupportedDrivers = function _getSupportedDrivers(drivers) {
            var supportedDrivers = [];
            for (var i = 0, len = drivers.length; i < len; i++) {
              var driverName = drivers[i];
              if (this.supports(driverName)) {
                supportedDrivers.push(driverName);
              }
            }
            return supportedDrivers;
          };
          LocalForage2.prototype._wrapLibraryMethodsWithReady = function _wrapLibraryMethodsWithReady() {
            for (var i = 0, len = LibraryMethods.length; i < len; i++) {
              callWhenReady(this, LibraryMethods[i]);
            }
          };
          LocalForage2.prototype.createInstance = function createInstance(options) {
            return new LocalForage2(options);
          };
          return LocalForage2;
        }();
        var localforage_js = new LocalForage();
        module3.exports = localforage_js;
      }, { "3": 3 }] }, {}, [4])(4);
    });
  }
});

// projects/aimmo-design-system/aim-select/src/aim-select-trigger.directive.ts
var AIM_SELECT_TRIGGER = new InjectionToken(" AimSelectTrigger");
var AimSelectTrigger = class AimSelectTrigger2 {
};
AimSelectTrigger = __decorate([
  Directive({
    selector: "aim-select-trigger, [aimSelectTrigger]",
    providers: [{ provide: AIM_SELECT_TRIGGER, useExisting: AimSelectTrigger }]
  })
], AimSelectTrigger);
var AIM_SELECT_PANEL_TRIGGER = new InjectionToken(" AimSelectPanelTrigger");
var AimSelectPanelTrigger = class AimSelectPanelTrigger2 {
};
AimSelectPanelTrigger = __decorate([
  Directive({
    selector: "[aimSelectPanelTrigger]",
    providers: [{ provide: AIM_SELECT_PANEL_TRIGGER, useExisting: AimSelectPanelTrigger }]
  })
], AimSelectPanelTrigger);

// angular:jit:template:file:projects/aimmo-design-system/aim-select/src/aim-select.component.html
var aim_select_component_default = `<ng-container *ngIf="!customPanelTrigger else customPanelTriggerTmpl">
  <aim-icon *ngIf="hasHeaderIcon" [icon]="headerIcon" class="aim-select__header-icon"/>
  <div [attr.id]="_valueId" class="aim-select__value">
    <span *ngIf="empty else selectedValuesTmpl"
          class="aim-select__placeholder aim-select--ellipsis">{{ placeholder }}</span>
  </div>
  <aim-icon [icon]="triggerIcon" class="aim-select__trigger-icon"/>
</ng-container>

<!--\uC140\uB809\uD2B8 \uD328\uB110 \uCEE4\uC2A4\uD140 \uD2B8\uB9AC\uAC70-->
<ng-template #customPanelTriggerTmpl>
  <ng-content select="[aimSelectPanelTrigger]"/>
</ng-template>

<!--\uC120\uD0DD \uC635\uC158 \uD45C\uC2DC \uCEE4\uC2A4\uD140 \uD2B8\uB9AC\uAC70-->
<ng-template #selectedValuesTmpl>
  <span *ngIf="!customTrigger else customTriggerTmpl"
        class="aim-select__value-text aim-select--ellipsis">{{ triggerValue }}</span>
  <ng-template #customTriggerTmpl>
    <ng-content select="aim-select-trigger, [aimSelectTrigger]"/>
  </ng-template>
</ng-template>


<!--\uC140\uB809\uD2B8 \uD328\uB110-->
<ng-template (attach)="_onAttached()"
             (backdropClick)="close()"
             (detach)="close()"
             [cdkConnectedOverlayLockPosition]="false"
             [cdkConnectedOverlayOffsetX]="overlayOffset.x"
             [cdkConnectedOverlayOffsetY]="overlayOffset.y"
             [cdkConnectedOverlayOpen]="panelOpen"
             [cdkConnectedOverlayOrigin]="overlayOrigin"
             [cdkConnectedOverlayPanelClass]="_overlayPanelClass"
             [cdkConnectedOverlayPositions]="_positions"
             [cdkConnectedOverlayScrollStrategy]="_scrollStrategy"
             [cdkConnectedOverlayWidth]="panelWidth"
             cdk-connected-overlay
             cdkConnectedOverlayBackdropClass="aim-select__backdrop"
             cdkConnectedOverlayHasBackdrop
             cdkConnectedOverlayPush>
  <div [class.project-filter]="responsivePanel" [class.table]="isTableContext"
       [ngClass]="customPanelClass" class="aim-select__panel-wrap">
    <!--_MatSelectBase\uC5D0\uC11C 'panel' \uD15C\uD50C\uB9BF \uBCC0\uC218\uB97C \uC0AC\uC6A9\uD558\uBBC0\uB85C \uC81C\uAC70X-->
    <div #panel
         (@aimTransformPanel.done)="_panelDoneAnimatingStream.next($event.toState)"
         (keydown)="_handleKeydown($event)"
         [@aimTransformPanel]="'showing'"
         [attr.aria-label]="ariaLabel || null"
         [attr.aria-labelledby]="panelAriaLabelledby()"
         [attr.aria-multiselectable]="multiple"
         [attr.id]="id + '-panel'"
         [ngClass]="panelClass"
         class="aim-select__panel {{panelTheme}}"
         role="listbox"
         tabindex="-1">
      <ng-content select="aim-all-select-option"/>
      <ng-content/>
    </div>
  </div>
</ng-template>
`;

// angular:jit:style:file:projects/aimmo-design-system/aim-select/src/aim-select.component.scss
var aim_select_component_default2 = "/* projects/aimmo-design-system/aim-select/src/aim-select.component.scss */\n:host {\n  display: inline-flex;\n  outline: none;\n}\n:host:not(.fit-content) {\n  box-sizing: border-box;\n  outline: none;\n  border: 1px solid transparent;\n  border-radius: 4px;\n  width: var(--select-field-width, 100%);\n  height: 32px;\n  padding: 0 16px;\n  align-items: center;\n  background-color: var(--aim-select-background-color, #333333);\n  font-family:\n    Pretendard,\n    Silka,\n    sans-serif;\n  font-weight: 400;\n  font-size: 14px;\n  line-height: 18px;\n  color: var(--aim-select-color, #dfdfdf);\n  cursor: var(--aim-cursor-hand-pointer, pointer);\n  -webkit-user-select: none;\n  user-select: none;\n}\n:host:not(.fit-content).table {\n  width: 100%;\n  height: 24px;\n  padding: 0 12px;\n}\n:host:not(.fit-content).table {\n  font-family:\n    Pretendard,\n    Silka,\n    sans-serif;\n  font-weight: 400;\n  font-size: 12px;\n  line-height: 14px;\n}\n:host:not(.fit-content):disabled,\n:host:not(.fit-content).aim-select--disabled {\n  background-color: #222222;\n  color: #545454;\n  cursor: not-allowed;\n}\n:host:not(.fit-content):disabled .aim-select__placeholder,\n:host:not(.fit-content).aim-select--disabled .aim-select__placeholder {\n  color: #545454;\n}\n:host:not(.fit-content):disabled .aim-select__trigger-icon,\n:host:not(.fit-content).aim-select--disabled .aim-select__trigger-icon {\n  color: #545454;\n}\n:host:not(.fit-content).aim-select:hover:not(:disabled, :host:not(.fit-content).aim-select--disabled, :host:not(.fit-content).aim-select--invalid, :host:not(.fit-content).aim-select--active) {\n  border-color: var(--aim-select-option-border-color-hover, #545454);\n}\n:host:not(.fit-content).aim-select:focus:not(:disabled, :host:not(.fit-content).aim-select--disabled, :host:not(.fit-content).aim-select--invalid) {\n  border-color: var(--aim-select-option-border-color-focus, #787878);\n}\n:host:not(.fit-content).aim-select--active:not(:disabled, :host:not(.fit-content).aim-select--disabled, :host:not(.fit-content).aim-select--invalid) {\n  border-color: var(--aim-select-option-border-color-active, #787878);\n}\n:host:not(.fit-content).aim-select--invalid:not(:disabled, :host:not(.fit-content).aim-select--disabled) {\n  border-color: #de6251;\n}\n.project-filter.aim-select__panel-wrap {\n  max-height: 100vh;\n  margin-left: 25px;\n}\n.project-filter.aim-select__panel-wrap ::ng-deep .aim-option__primary-text {\n  letter-spacing: -0.18px;\n}\n.aim-select--ellipsis {\n  overflow: hidden;\n  text-overflow: ellipsis;\n  white-space: nowrap;\n}\n.aim-select__header-icon {\n  margin-right: 8px;\n}\n.aim-select__value {\n  display: inline-flex;\n  width: 100%;\n  margin-right: 8px;\n  overflow: hidden;\n}\n.aim-select__placeholder {\n  color: #787878;\n}\n.aim-select__trigger-icon {\n  color: var(--aim-select-trigger-icon-color, #dfdfdf);\n  text-align: end;\n}\n.aim-select__panel-wrap {\n  box-sizing: border-box;\n  outline: none;\n  border: 1px solid transparent;\n  border-radius: 4px;\n  border: 1px solid transparent;\n  width: 100%;\n  max-height: 154px;\n  padding: 4px 0;\n  border-color: var(--aim-select-panel-border-color, rgba(0, 0, 0, 0.35));\n  background-color: var(--aim-select-panel-background-color, #222222);\n}\n.aim-select__panel-wrap.table {\n  max-height: 116px;\n}\n.aim-select__panel {\n  height: 100%;\n  outline: none;\n  overflow-y: auto;\n  -ms-overflow-style: none;\n}\n.aim-select__panel::-webkit-scrollbar {\n  display: none;\n  width: 0 !important;\n}\n::ng-deep .aim-select__backdrop.cdk-overlay-backdrop-showing {\n  opacity: 0;\n}\n";

// node_modules/@angular/material/fesm2022/select.mjs
var matSelectAnimations = {
  /**
   * This animation ensures the select's overlay panel animation (transformPanel) is called when
   * closing the select.
   * This is needed due to https://github.com/angular/angular/issues/23302
   */
  transformPanelWrap: trigger("transformPanelWrap", [
    transition("* => void", query("@transformPanel", [animateChild()], { optional: true }))
  ]),
  /** This animation transforms the select's overlay panel on and off the page. */
  transformPanel: trigger("transformPanel", [
    state("void", style({
      opacity: 0,
      transform: "scale(1, 0.8)"
    })),
    transition("void => showing", animate("120ms cubic-bezier(0, 0, 0.2, 1)", style({
      opacity: 1,
      transform: "scale(1, 1)"
    }))),
    transition("* => void", animate("100ms linear", style({ opacity: 0 })))
  ])
};
function getMatSelectDynamicMultipleError() {
  return Error("Cannot change `multiple` mode of select after initialization.");
}
function getMatSelectNonArrayValueError() {
  return Error("Value must be an array in multiple-selection mode.");
}
function getMatSelectNonFunctionValueError() {
  return Error("`compareWith` must be a function.");
}
var nextUniqueId = 0;
var MAT_SELECT_SCROLL_STRATEGY = new InjectionToken("mat-select-scroll-strategy", {
  providedIn: "root",
  factory: () => {
    const overlay = inject(Overlay);
    return () => overlay.scrollStrategies.reposition();
  }
});
function MAT_SELECT_SCROLL_STRATEGY_PROVIDER_FACTORY(overlay) {
  return () => overlay.scrollStrategies.reposition();
}
var MAT_SELECT_CONFIG = new InjectionToken("MAT_SELECT_CONFIG");
var MAT_SELECT_SCROLL_STRATEGY_PROVIDER = {
  provide: MAT_SELECT_SCROLL_STRATEGY,
  deps: [Overlay],
  useFactory: MAT_SELECT_SCROLL_STRATEGY_PROVIDER_FACTORY
};
var MAT_SELECT_TRIGGER = new InjectionToken("MatSelectTrigger");
var MatSelectChange = class {
  constructor(source, value) {
    this.source = source;
    this.value = value;
  }
};
var _MatSelect = class _MatSelect {
  /** Scrolls a particular option into the view. */
  _scrollOptionIntoView(index) {
    const option = this.options.toArray()[index];
    if (option) {
      const panel = this.panel.nativeElement;
      const labelCount = _countGroupLabelsBeforeOption(index, this.options, this.optionGroups);
      const element = option._getHostElement();
      if (index === 0 && labelCount === 1) {
        panel.scrollTop = 0;
      } else {
        panel.scrollTop = _getOptionScrollPosition(element.offsetTop, element.offsetHeight, panel.scrollTop, panel.offsetHeight);
      }
    }
  }
  /** Called when the panel has been opened and the overlay has settled on its final position. */
  _positioningSettled() {
    this._scrollOptionIntoView(this._keyManager.activeItemIndex || 0);
  }
  /** Creates a change event object that should be emitted by the select. */
  _getChangeEvent(value) {
    return new MatSelectChange(this, value);
  }
  /** Whether the select is focused. */
  get focused() {
    return this._focused || this._panelOpen;
  }
  /** Whether checkmark indicator for single-selection options is hidden. */
  get hideSingleSelectionIndicator() {
    return this._hideSingleSelectionIndicator;
  }
  set hideSingleSelectionIndicator(value) {
    this._hideSingleSelectionIndicator = value;
    this._syncParentProperties();
  }
  /** Placeholder to be shown if no value has been selected. */
  get placeholder() {
    return this._placeholder;
  }
  set placeholder(value) {
    this._placeholder = value;
    this.stateChanges.next();
  }
  /** Whether the component is required. */
  get required() {
    return this._required ?? this.ngControl?.control?.hasValidator(Validators.required) ?? false;
  }
  set required(value) {
    this._required = value;
    this.stateChanges.next();
  }
  /** Whether the user should be allowed to select multiple options. */
  get multiple() {
    return this._multiple;
  }
  set multiple(value) {
    if (this._selectionModel && (typeof ngDevMode === "undefined" || ngDevMode)) {
      throw getMatSelectDynamicMultipleError();
    }
    this._multiple = value;
  }
  /**
   * Function to compare the option values with the selected values. The first argument
   * is a value from an option. The second is a value from the selection. A boolean
   * should be returned.
   */
  get compareWith() {
    return this._compareWith;
  }
  set compareWith(fn) {
    if (typeof fn !== "function" && (typeof ngDevMode === "undefined" || ngDevMode)) {
      throw getMatSelectNonFunctionValueError();
    }
    this._compareWith = fn;
    if (this._selectionModel) {
      this._initializeSelection();
    }
  }
  /** Value of the select control. */
  get value() {
    return this._value;
  }
  set value(newValue) {
    const hasAssigned = this._assignValue(newValue);
    if (hasAssigned) {
      this._onChange(newValue);
    }
  }
  /** Object used to control when error messages are shown. */
  get errorStateMatcher() {
    return this._errorStateTracker.matcher;
  }
  set errorStateMatcher(value) {
    this._errorStateTracker.matcher = value;
  }
  /** Unique id of the element. */
  get id() {
    return this._id;
  }
  set id(value) {
    this._id = value || this._uid;
    this.stateChanges.next();
  }
  /** Whether the select is in an error state. */
  get errorState() {
    return this._errorStateTracker.errorState;
  }
  set errorState(value) {
    this._errorStateTracker.errorState = value;
  }
  constructor(_viewportRuler, _changeDetectorRef, _unusedNgZone, defaultErrorStateMatcher, _elementRef, _dir, parentForm, parentFormGroup, _parentFormField, ngControl, tabIndex, scrollStrategyFactory, _liveAnnouncer, _defaultOptions) {
    this._viewportRuler = _viewportRuler;
    this._changeDetectorRef = _changeDetectorRef;
    this._elementRef = _elementRef;
    this._dir = _dir;
    this._parentFormField = _parentFormField;
    this.ngControl = ngControl;
    this._liveAnnouncer = _liveAnnouncer;
    this._defaultOptions = _defaultOptions;
    this._positions = [
      {
        originX: "start",
        originY: "bottom",
        overlayX: "start",
        overlayY: "top"
      },
      {
        originX: "end",
        originY: "bottom",
        overlayX: "end",
        overlayY: "top"
      },
      {
        originX: "start",
        originY: "top",
        overlayX: "start",
        overlayY: "bottom",
        panelClass: "mat-mdc-select-panel-above"
      },
      {
        originX: "end",
        originY: "top",
        overlayX: "end",
        overlayY: "bottom",
        panelClass: "mat-mdc-select-panel-above"
      }
    ];
    this._panelOpen = false;
    this._compareWith = (o1, o2) => o1 === o2;
    this._uid = `mat-select-${nextUniqueId++}`;
    this._triggerAriaLabelledBy = null;
    this._destroy = new Subject();
    this.stateChanges = new Subject();
    this.disableAutomaticLabeling = true;
    this._onChange = () => {
    };
    this._onTouched = () => {
    };
    this._valueId = `mat-select-value-${nextUniqueId++}`;
    this._panelDoneAnimatingStream = new Subject();
    this._overlayPanelClass = this._defaultOptions?.overlayPanelClass || "";
    this._focused = false;
    this.controlType = "mat-select";
    this.disabled = false;
    this.disableRipple = false;
    this.tabIndex = 0;
    this._hideSingleSelectionIndicator = this._defaultOptions?.hideSingleSelectionIndicator ?? false;
    this._multiple = false;
    this.disableOptionCentering = this._defaultOptions?.disableOptionCentering ?? false;
    this.ariaLabel = "";
    this.panelWidth = this._defaultOptions && typeof this._defaultOptions.panelWidth !== "undefined" ? this._defaultOptions.panelWidth : "auto";
    this._initialized = new Subject();
    this.optionSelectionChanges = defer(() => {
      const options = this.options;
      if (options) {
        return options.changes.pipe(startWith(options), switchMap(() => merge(...options.map((option) => option.onSelectionChange))));
      }
      return this._initialized.pipe(switchMap(() => this.optionSelectionChanges));
    });
    this.openedChange = new EventEmitter();
    this._openedStream = this.openedChange.pipe(filter((o) => o), map(() => {
    }));
    this._closedStream = this.openedChange.pipe(filter((o) => !o), map(() => {
    }));
    this.selectionChange = new EventEmitter();
    this.valueChange = new EventEmitter();
    this._trackedModal = null;
    this._skipPredicate = (option) => {
      if (this.panelOpen) {
        return false;
      }
      return option.disabled;
    };
    if (this.ngControl) {
      this.ngControl.valueAccessor = this;
    }
    if (_defaultOptions?.typeaheadDebounceInterval != null) {
      this.typeaheadDebounceInterval = _defaultOptions.typeaheadDebounceInterval;
    }
    this._errorStateTracker = new _ErrorStateTracker(defaultErrorStateMatcher, ngControl, parentFormGroup, parentForm, this.stateChanges);
    this._scrollStrategyFactory = scrollStrategyFactory;
    this._scrollStrategy = this._scrollStrategyFactory();
    this.tabIndex = parseInt(tabIndex) || 0;
    this.id = this.id;
  }
  ngOnInit() {
    this._selectionModel = new SelectionModel(this.multiple);
    this.stateChanges.next();
    this._panelDoneAnimatingStream.pipe(distinctUntilChanged(), takeUntil(this._destroy)).subscribe(() => this._panelDoneAnimating(this.panelOpen));
    this._viewportRuler.change().pipe(takeUntil(this._destroy)).subscribe(() => {
      if (this.panelOpen) {
        this._overlayWidth = this._getOverlayWidth(this._preferredOverlayOrigin);
        this._changeDetectorRef.detectChanges();
      }
    });
  }
  ngAfterContentInit() {
    this._initialized.next();
    this._initialized.complete();
    this._initKeyManager();
    this._selectionModel.changed.pipe(takeUntil(this._destroy)).subscribe((event) => {
      event.added.forEach((option) => option.select());
      event.removed.forEach((option) => option.deselect());
    });
    this.options.changes.pipe(startWith(null), takeUntil(this._destroy)).subscribe(() => {
      this._resetOptions();
      this._initializeSelection();
    });
  }
  ngDoCheck() {
    const newAriaLabelledby = this._getTriggerAriaLabelledby();
    const ngControl = this.ngControl;
    if (newAriaLabelledby !== this._triggerAriaLabelledBy) {
      const element = this._elementRef.nativeElement;
      this._triggerAriaLabelledBy = newAriaLabelledby;
      if (newAriaLabelledby) {
        element.setAttribute("aria-labelledby", newAriaLabelledby);
      } else {
        element.removeAttribute("aria-labelledby");
      }
    }
    if (ngControl) {
      if (this._previousControl !== ngControl.control) {
        if (this._previousControl !== void 0 && ngControl.disabled !== null && ngControl.disabled !== this.disabled) {
          this.disabled = ngControl.disabled;
        }
        this._previousControl = ngControl.control;
      }
      this.updateErrorState();
    }
  }
  ngOnChanges(changes) {
    if (changes["disabled"] || changes["userAriaDescribedBy"]) {
      this.stateChanges.next();
    }
    if (changes["typeaheadDebounceInterval"] && this._keyManager) {
      this._keyManager.withTypeAhead(this.typeaheadDebounceInterval);
    }
  }
  ngOnDestroy() {
    this._keyManager?.destroy();
    this._destroy.next();
    this._destroy.complete();
    this.stateChanges.complete();
    this._clearFromModal();
  }
  /** Toggles the overlay panel open or closed. */
  toggle() {
    this.panelOpen ? this.close() : this.open();
  }
  /** Opens the overlay panel. */
  open() {
    if (!this._canOpen()) {
      return;
    }
    if (this._parentFormField) {
      this._preferredOverlayOrigin = this._parentFormField.getConnectedOverlayOrigin();
    }
    this._overlayWidth = this._getOverlayWidth(this._preferredOverlayOrigin);
    this._applyModalPanelOwnership();
    this._panelOpen = true;
    this._keyManager.withHorizontalOrientation(null);
    this._highlightCorrectOption();
    this._changeDetectorRef.markForCheck();
    this.stateChanges.next();
  }
  /**
   * If the autocomplete trigger is inside of an `aria-modal` element, connect
   * that modal to the options panel with `aria-owns`.
   *
   * For some browser + screen reader combinations, when navigation is inside
   * of an `aria-modal` element, the screen reader treats everything outside
   * of that modal as hidden or invisible.
   *
   * This causes a problem when the combobox trigger is _inside_ of a modal, because the
   * options panel is rendered _outside_ of that modal, preventing screen reader navigation
   * from reaching the panel.
   *
   * We can work around this issue by applying `aria-owns` to the modal with the `id` of
   * the options panel. This effectively communicates to assistive technology that the
   * options panel is part of the same interaction as the modal.
   *
   * At time of this writing, this issue is present in VoiceOver.
   * See https://github.com/angular/components/issues/20694
   */
  _applyModalPanelOwnership() {
    const modal = this._elementRef.nativeElement.closest('body > .cdk-overlay-container [aria-modal="true"]');
    if (!modal) {
      return;
    }
    const panelId = `${this.id}-panel`;
    if (this._trackedModal) {
      removeAriaReferencedId(this._trackedModal, "aria-owns", panelId);
    }
    addAriaReferencedId(modal, "aria-owns", panelId);
    this._trackedModal = modal;
  }
  /** Clears the reference to the listbox overlay element from the modal it was added to. */
  _clearFromModal() {
    if (!this._trackedModal) {
      return;
    }
    const panelId = `${this.id}-panel`;
    removeAriaReferencedId(this._trackedModal, "aria-owns", panelId);
    this._trackedModal = null;
  }
  /** Closes the overlay panel and focuses the host element. */
  close() {
    if (this._panelOpen) {
      this._panelOpen = false;
      this._keyManager.withHorizontalOrientation(this._isRtl() ? "rtl" : "ltr");
      this._changeDetectorRef.markForCheck();
      this._onTouched();
      this.stateChanges.next();
    }
  }
  /**
   * Sets the select's value. Part of the ControlValueAccessor interface
   * required to integrate with Angular's core forms API.
   *
   * @param value New value to be written to the model.
   */
  writeValue(value) {
    this._assignValue(value);
  }
  /**
   * Saves a callback function to be invoked when the select's value
   * changes from user input. Part of the ControlValueAccessor interface
   * required to integrate with Angular's core forms API.
   *
   * @param fn Callback to be triggered when the value changes.
   */
  registerOnChange(fn) {
    this._onChange = fn;
  }
  /**
   * Saves a callback function to be invoked when the select is blurred
   * by the user. Part of the ControlValueAccessor interface required
   * to integrate with Angular's core forms API.
   *
   * @param fn Callback to be triggered when the component has been touched.
   */
  registerOnTouched(fn) {
    this._onTouched = fn;
  }
  /**
   * Disables the select. Part of the ControlValueAccessor interface required
   * to integrate with Angular's core forms API.
   *
   * @param isDisabled Sets whether the component is disabled.
   */
  setDisabledState(isDisabled) {
    this.disabled = isDisabled;
    this._changeDetectorRef.markForCheck();
    this.stateChanges.next();
  }
  /** Whether or not the overlay panel is open. */
  get panelOpen() {
    return this._panelOpen;
  }
  /** The currently selected option. */
  get selected() {
    return this.multiple ? this._selectionModel?.selected || [] : this._selectionModel?.selected[0];
  }
  /** The value displayed in the trigger. */
  get triggerValue() {
    if (this.empty) {
      return "";
    }
    if (this._multiple) {
      const selectedOptions = this._selectionModel.selected.map((option) => option.viewValue);
      if (this._isRtl()) {
        selectedOptions.reverse();
      }
      return selectedOptions.join(", ");
    }
    return this._selectionModel.selected[0].viewValue;
  }
  /** Refreshes the error state of the select. */
  updateErrorState() {
    this._errorStateTracker.updateErrorState();
  }
  /** Whether the element is in RTL mode. */
  _isRtl() {
    return this._dir ? this._dir.value === "rtl" : false;
  }
  /** Handles all keydown events on the select. */
  _handleKeydown(event) {
    if (!this.disabled) {
      this.panelOpen ? this._handleOpenKeydown(event) : this._handleClosedKeydown(event);
    }
  }
  /** Handles keyboard events while the select is closed. */
  _handleClosedKeydown(event) {
    const keyCode = event.keyCode;
    const isArrowKey = keyCode === DOWN_ARROW || keyCode === UP_ARROW || keyCode === LEFT_ARROW || keyCode === RIGHT_ARROW;
    const isOpenKey = keyCode === ENTER || keyCode === SPACE;
    const manager = this._keyManager;
    if (!manager.isTyping() && isOpenKey && !hasModifierKey(event) || (this.multiple || event.altKey) && isArrowKey) {
      event.preventDefault();
      this.open();
    } else if (!this.multiple) {
      const previouslySelectedOption = this.selected;
      manager.onKeydown(event);
      const selectedOption = this.selected;
      if (selectedOption && previouslySelectedOption !== selectedOption) {
        this._liveAnnouncer.announce(selectedOption.viewValue, 1e4);
      }
    }
  }
  /** Handles keyboard events when the selected is open. */
  _handleOpenKeydown(event) {
    const manager = this._keyManager;
    const keyCode = event.keyCode;
    const isArrowKey = keyCode === DOWN_ARROW || keyCode === UP_ARROW;
    const isTyping = manager.isTyping();
    if (isArrowKey && event.altKey) {
      event.preventDefault();
      this.close();
    } else if (!isTyping && (keyCode === ENTER || keyCode === SPACE) && manager.activeItem && !hasModifierKey(event)) {
      event.preventDefault();
      manager.activeItem._selectViaInteraction();
    } else if (!isTyping && this._multiple && keyCode === A && event.ctrlKey) {
      event.preventDefault();
      const hasDeselectedOptions = this.options.some((opt) => !opt.disabled && !opt.selected);
      this.options.forEach((option) => {
        if (!option.disabled) {
          hasDeselectedOptions ? option.select() : option.deselect();
        }
      });
    } else {
      const previouslyFocusedIndex = manager.activeItemIndex;
      manager.onKeydown(event);
      if (this._multiple && isArrowKey && event.shiftKey && manager.activeItem && manager.activeItemIndex !== previouslyFocusedIndex) {
        manager.activeItem._selectViaInteraction();
      }
    }
  }
  _onFocus() {
    if (!this.disabled) {
      this._focused = true;
      this.stateChanges.next();
    }
  }
  /**
   * Calls the touched callback only if the panel is closed. Otherwise, the trigger will
   * "blur" to the panel when it opens, causing a false positive.
   */
  _onBlur() {
    this._focused = false;
    this._keyManager?.cancelTypeahead();
    if (!this.disabled && !this.panelOpen) {
      this._onTouched();
      this._changeDetectorRef.markForCheck();
      this.stateChanges.next();
    }
  }
  /**
   * Callback that is invoked when the overlay panel has been attached.
   */
  _onAttached() {
    this._overlayDir.positionChange.pipe(take(1)).subscribe(() => {
      this._changeDetectorRef.detectChanges();
      this._positioningSettled();
    });
  }
  /** Returns the theme to be used on the panel. */
  _getPanelTheme() {
    return this._parentFormField ? `mat-${this._parentFormField.color}` : "";
  }
  /** Whether the select has a value. */
  get empty() {
    return !this._selectionModel || this._selectionModel.isEmpty();
  }
  _initializeSelection() {
    Promise.resolve().then(() => {
      if (this.ngControl) {
        this._value = this.ngControl.value;
      }
      this._setSelectionByValue(this._value);
      this.stateChanges.next();
    });
  }
  /**
   * Sets the selected option based on a value. If no option can be
   * found with the designated value, the select trigger is cleared.
   */
  _setSelectionByValue(value) {
    this.options.forEach((option) => option.setInactiveStyles());
    this._selectionModel.clear();
    if (this.multiple && value) {
      if (!Array.isArray(value) && (typeof ngDevMode === "undefined" || ngDevMode)) {
        throw getMatSelectNonArrayValueError();
      }
      value.forEach((currentValue) => this._selectOptionByValue(currentValue));
      this._sortValues();
    } else {
      const correspondingOption = this._selectOptionByValue(value);
      if (correspondingOption) {
        this._keyManager.updateActiveItem(correspondingOption);
      } else if (!this.panelOpen) {
        this._keyManager.updateActiveItem(-1);
      }
    }
    this._changeDetectorRef.markForCheck();
  }
  /**
   * Finds and selects and option based on its value.
   * @returns Option that has the corresponding value.
   */
  _selectOptionByValue(value) {
    const correspondingOption = this.options.find((option) => {
      if (this._selectionModel.isSelected(option)) {
        return false;
      }
      try {
        return option.value != null && this._compareWith(option.value, value);
      } catch (error) {
        if (typeof ngDevMode === "undefined" || ngDevMode) {
          console.warn(error);
        }
        return false;
      }
    });
    if (correspondingOption) {
      this._selectionModel.select(correspondingOption);
    }
    return correspondingOption;
  }
  /** Assigns a specific value to the select. Returns whether the value has changed. */
  _assignValue(newValue) {
    if (newValue !== this._value || this._multiple && Array.isArray(newValue)) {
      if (this.options) {
        this._setSelectionByValue(newValue);
      }
      this._value = newValue;
      return true;
    }
    return false;
  }
  /** Gets how wide the overlay panel should be. */
  _getOverlayWidth(preferredOrigin) {
    if (this.panelWidth === "auto") {
      const refToMeasure = preferredOrigin instanceof CdkOverlayOrigin ? preferredOrigin.elementRef : preferredOrigin || this._elementRef;
      return refToMeasure.nativeElement.getBoundingClientRect().width;
    }
    return this.panelWidth === null ? "" : this.panelWidth;
  }
  /** Syncs the parent state with the individual options. */
  _syncParentProperties() {
    if (this.options) {
      for (const option of this.options) {
        option._changeDetectorRef.markForCheck();
      }
    }
  }
  /** Sets up a key manager to listen to keyboard events on the overlay panel. */
  _initKeyManager() {
    this._keyManager = new ActiveDescendantKeyManager(this.options).withTypeAhead(this.typeaheadDebounceInterval).withVerticalOrientation().withHorizontalOrientation(this._isRtl() ? "rtl" : "ltr").withHomeAndEnd().withPageUpDown().withAllowedModifierKeys(["shiftKey"]).skipPredicate(this._skipPredicate);
    this._keyManager.tabOut.subscribe(() => {
      if (this.panelOpen) {
        if (!this.multiple && this._keyManager.activeItem) {
          this._keyManager.activeItem._selectViaInteraction();
        }
        this.focus();
        this.close();
      }
    });
    this._keyManager.change.subscribe(() => {
      if (this._panelOpen && this.panel) {
        this._scrollOptionIntoView(this._keyManager.activeItemIndex || 0);
      } else if (!this._panelOpen && !this.multiple && this._keyManager.activeItem) {
        this._keyManager.activeItem._selectViaInteraction();
      }
    });
  }
  /** Drops current option subscriptions and IDs and resets from scratch. */
  _resetOptions() {
    const changedOrDestroyed = merge(this.options.changes, this._destroy);
    this.optionSelectionChanges.pipe(takeUntil(changedOrDestroyed)).subscribe((event) => {
      this._onSelect(event.source, event.isUserInput);
      if (event.isUserInput && !this.multiple && this._panelOpen) {
        this.close();
        this.focus();
      }
    });
    merge(...this.options.map((option) => option._stateChanges)).pipe(takeUntil(changedOrDestroyed)).subscribe(() => {
      this._changeDetectorRef.detectChanges();
      this.stateChanges.next();
    });
  }
  /** Invoked when an option is clicked. */
  _onSelect(option, isUserInput) {
    const wasSelected = this._selectionModel.isSelected(option);
    if (option.value == null && !this._multiple) {
      option.deselect();
      this._selectionModel.clear();
      if (this.value != null) {
        this._propagateChanges(option.value);
      }
    } else {
      if (wasSelected !== option.selected) {
        option.selected ? this._selectionModel.select(option) : this._selectionModel.deselect(option);
      }
      if (isUserInput) {
        this._keyManager.setActiveItem(option);
      }
      if (this.multiple) {
        this._sortValues();
        if (isUserInput) {
          this.focus();
        }
      }
    }
    if (wasSelected !== this._selectionModel.isSelected(option)) {
      this._propagateChanges();
    }
    this.stateChanges.next();
  }
  /** Sorts the selected values in the selected based on their order in the panel. */
  _sortValues() {
    if (this.multiple) {
      const options = this.options.toArray();
      this._selectionModel.sort((a, b) => {
        return this.sortComparator ? this.sortComparator(a, b, options) : options.indexOf(a) - options.indexOf(b);
      });
      this.stateChanges.next();
    }
  }
  /** Emits change event to set the model value. */
  _propagateChanges(fallbackValue) {
    let valueToEmit;
    if (this.multiple) {
      valueToEmit = this.selected.map((option) => option.value);
    } else {
      valueToEmit = this.selected ? this.selected.value : fallbackValue;
    }
    this._value = valueToEmit;
    this.valueChange.emit(valueToEmit);
    this._onChange(valueToEmit);
    this.selectionChange.emit(this._getChangeEvent(valueToEmit));
    this._changeDetectorRef.markForCheck();
  }
  /**
   * Highlights the selected item. If no option is selected, it will highlight
   * the first *enabled* option.
   */
  _highlightCorrectOption() {
    if (this._keyManager) {
      if (this.empty) {
        let firstEnabledOptionIndex = -1;
        for (let index = 0; index < this.options.length; index++) {
          const option = this.options.get(index);
          if (!option.disabled) {
            firstEnabledOptionIndex = index;
            break;
          }
        }
        this._keyManager.setActiveItem(firstEnabledOptionIndex);
      } else {
        this._keyManager.setActiveItem(this._selectionModel.selected[0]);
      }
    }
  }
  /** Whether the panel is allowed to open. */
  _canOpen() {
    return !this._panelOpen && !this.disabled && this.options?.length > 0;
  }
  /** Focuses the select element. */
  focus(options) {
    this._elementRef.nativeElement.focus(options);
  }
  /** Gets the aria-labelledby for the select panel. */
  _getPanelAriaLabelledby() {
    if (this.ariaLabel) {
      return null;
    }
    const labelId = this._parentFormField?.getLabelId();
    const labelExpression = labelId ? labelId + " " : "";
    return this.ariaLabelledby ? labelExpression + this.ariaLabelledby : labelId;
  }
  /** Determines the `aria-activedescendant` to be set on the host. */
  _getAriaActiveDescendant() {
    if (this.panelOpen && this._keyManager && this._keyManager.activeItem) {
      return this._keyManager.activeItem.id;
    }
    return null;
  }
  /** Gets the aria-labelledby of the select component trigger. */
  _getTriggerAriaLabelledby() {
    if (this.ariaLabel) {
      return null;
    }
    const labelId = this._parentFormField?.getLabelId();
    let value = (labelId ? labelId + " " : "") + this._valueId;
    if (this.ariaLabelledby) {
      value += " " + this.ariaLabelledby;
    }
    return value;
  }
  /** Called when the overlay panel is done animating. */
  _panelDoneAnimating(isOpen) {
    this.openedChange.emit(isOpen);
  }
  /**
   * Implemented as part of MatFormFieldControl.
   * @docs-private
   */
  setDescribedByIds(ids) {
    if (ids.length) {
      this._elementRef.nativeElement.setAttribute("aria-describedby", ids.join(" "));
    } else {
      this._elementRef.nativeElement.removeAttribute("aria-describedby");
    }
  }
  /**
   * Implemented as part of MatFormFieldControl.
   * @docs-private
   */
  onContainerClick() {
    this.focus();
    this.open();
  }
  /**
   * Implemented as part of MatFormFieldControl.
   * @docs-private
   */
  get shouldLabelFloat() {
    return this.panelOpen || !this.empty || this.focused && !!this.placeholder;
  }
};
_MatSelect.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: _MatSelect, deps: [{ token: ViewportRuler }, { token: ChangeDetectorRef }, { token: NgZone }, { token: ErrorStateMatcher }, { token: ElementRef }, { token: Directionality, optional: true }, { token: NgForm, optional: true }, { token: FormGroupDirective, optional: true }, { token: MAT_FORM_FIELD, optional: true }, { token: NgControl, optional: true, self: true }, { token: "tabindex", attribute: true }, { token: MAT_SELECT_SCROLL_STRATEGY }, { token: LiveAnnouncer }, { token: MAT_SELECT_CONFIG, optional: true }], target: FactoryTarget.Component });
_MatSelect.\u0275cmp = \u0275\u0275ngDeclareComponent({ minVersion: "17.0.0", version: "17.2.0", type: _MatSelect, isStandalone: true, selector: "mat-select", inputs: { userAriaDescribedBy: ["aria-describedby", "userAriaDescribedBy"], panelClass: "panelClass", disabled: ["disabled", "disabled", booleanAttribute], disableRipple: ["disableRipple", "disableRipple", booleanAttribute], tabIndex: ["tabIndex", "tabIndex", (value) => value == null ? 0 : numberAttribute(value)], hideSingleSelectionIndicator: ["hideSingleSelectionIndicator", "hideSingleSelectionIndicator", booleanAttribute], placeholder: "placeholder", required: ["required", "required", booleanAttribute], multiple: ["multiple", "multiple", booleanAttribute], disableOptionCentering: ["disableOptionCentering", "disableOptionCentering", booleanAttribute], compareWith: "compareWith", value: "value", ariaLabel: ["aria-label", "ariaLabel"], ariaLabelledby: ["aria-labelledby", "ariaLabelledby"], errorStateMatcher: "errorStateMatcher", typeaheadDebounceInterval: ["typeaheadDebounceInterval", "typeaheadDebounceInterval", numberAttribute], sortComparator: "sortComparator", id: "id", panelWidth: "panelWidth" }, outputs: { openedChange: "openedChange", _openedStream: "opened", _closedStream: "closed", selectionChange: "selectionChange", valueChange: "valueChange" }, host: { attributes: { "role": "combobox", "aria-autocomplete": "none", "aria-haspopup": "listbox" }, listeners: { "keydown": "_handleKeydown($event)", "focus": "_onFocus()", "blur": "_onBlur()" }, properties: { "attr.id": "id", "attr.tabindex": "disabled ? -1 : tabIndex", "attr.aria-controls": 'panelOpen ? id + "-panel" : null', "attr.aria-expanded": "panelOpen", "attr.aria-label": "ariaLabel || null", "attr.aria-required": "required.toString()", "attr.aria-disabled": "disabled.toString()", "attr.aria-invalid": "errorState", "attr.aria-activedescendant": "_getAriaActiveDescendant()", "class.mat-mdc-select-disabled": "disabled", "class.mat-mdc-select-invalid": "errorState", "class.mat-mdc-select-required": "required", "class.mat-mdc-select-empty": "empty", "class.mat-mdc-select-multiple": "multiple" }, classAttribute: "mat-mdc-select" }, providers: [
  { provide: MatFormFieldControl, useExisting: _MatSelect },
  { provide: MAT_OPTION_PARENT_COMPONENT, useExisting: _MatSelect }
], queries: [{ propertyName: "customTrigger", first: true, predicate: MAT_SELECT_TRIGGER, descendants: true }, { propertyName: "options", predicate: MatOption, descendants: true }, { propertyName: "optionGroups", predicate: MAT_OPTGROUP, descendants: true }], viewQueries: [{ propertyName: "trigger", first: true, predicate: ["trigger"], descendants: true }, { propertyName: "panel", first: true, predicate: ["panel"], descendants: true }, { propertyName: "_overlayDir", first: true, predicate: CdkConnectedOverlay, descendants: true }], exportAs: ["matSelect"], usesOnChanges: true, ngImport: core_exports, template: `<div cdk-overlay-origin
     class="mat-mdc-select-trigger"
     (click)="open()"
     #fallbackOverlayOrigin="cdkOverlayOrigin"
     #trigger>

  <div class="mat-mdc-select-value" [attr.id]="_valueId">
    @if (empty) {
      <span class="mat-mdc-select-placeholder mat-mdc-select-min-line">{{placeholder}}</span>
    } @else {
      <span class="mat-mdc-select-value-text">
        @if (customTrigger) {
          <ng-content select="mat-select-trigger"></ng-content>
        } @else {
          <span class="mat-mdc-select-min-line">{{triggerValue}}</span>
        }
      </span>
    }
  </div>

  <div class="mat-mdc-select-arrow-wrapper">
    <div class="mat-mdc-select-arrow">
      <!-- Use an inline SVG, because it works better than a CSS triangle in high contrast mode. -->
      <svg viewBox="0 0 24 24" width="24px" height="24px" focusable="false" aria-hidden="true">
        <path d="M7 10l5 5 5-5z"/>
      </svg>
    </div>
  </div>
</div>

<ng-template
  cdk-connected-overlay
  cdkConnectedOverlayLockPosition
  cdkConnectedOverlayHasBackdrop
  cdkConnectedOverlayBackdropClass="cdk-overlay-transparent-backdrop"
  [cdkConnectedOverlayPanelClass]="_overlayPanelClass"
  [cdkConnectedOverlayScrollStrategy]="_scrollStrategy"
  [cdkConnectedOverlayOrigin]="_preferredOverlayOrigin || fallbackOverlayOrigin"
  [cdkConnectedOverlayOpen]="panelOpen"
  [cdkConnectedOverlayPositions]="_positions"
  [cdkConnectedOverlayWidth]="_overlayWidth"
  (backdropClick)="close()"
  (attach)="_onAttached()"
  (detach)="close()">
  <div
    #panel
    role="listbox"
    tabindex="-1"
    class="mat-mdc-select-panel mdc-menu-surface mdc-menu-surface--open {{ _getPanelTheme() }}"
    [attr.id]="id + '-panel'"
    [attr.aria-multiselectable]="multiple"
    [attr.aria-label]="ariaLabel || null"
    [attr.aria-labelledby]="_getPanelAriaLabelledby()"
    [ngClass]="panelClass"
    [@transformPanel]="'showing'"
    (@transformPanel.done)="_panelDoneAnimatingStream.next($event.toState)"
    (keydown)="_handleKeydown($event)">
    <ng-content></ng-content>
  </div>
</ng-template>
`, styles: ['.mat-mdc-select{display:inline-block;width:100%;outline:none;-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;color:var(--mat-select-enabled-trigger-text-color);font-family:var(--mat-select-trigger-text-font);line-height:var(--mat-select-trigger-text-line-height);font-size:var(--mat-select-trigger-text-size);font-weight:var(--mat-select-trigger-text-weight);letter-spacing:var(--mat-select-trigger-text-tracking)}div.mat-mdc-select-panel{box-shadow:var(--mat-select-container-elevation-shadow)}.mat-mdc-select-disabled{color:var(--mat-select-disabled-trigger-text-color)}.mat-mdc-select-trigger{display:inline-flex;align-items:center;cursor:pointer;position:relative;box-sizing:border-box;width:100%}.mat-mdc-select-disabled .mat-mdc-select-trigger{-webkit-user-select:none;user-select:none;cursor:default}.mat-mdc-select-value{width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.mat-mdc-select-value-text{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mat-mdc-select-arrow-wrapper{height:24px;flex-shrink:0;display:inline-flex;align-items:center}.mat-form-field-appearance-fill .mdc-text-field--no-label .mat-mdc-select-arrow-wrapper{transform:none}.mat-mdc-form-field .mat-mdc-select.mat-mdc-select-invalid .mat-mdc-select-arrow,.mat-form-field-invalid:not(.mat-form-field-disabled) .mat-mdc-form-field-infix::after{color:var(--mat-select-invalid-arrow-color)}.mat-mdc-select-arrow{width:10px;height:5px;position:relative;color:var(--mat-select-enabled-arrow-color)}.mat-mdc-form-field.mat-focused .mat-mdc-select-arrow{color:var(--mat-select-focused-arrow-color)}.mat-mdc-form-field .mat-mdc-select.mat-mdc-select-disabled .mat-mdc-select-arrow{color:var(--mat-select-disabled-arrow-color)}.mat-mdc-select-arrow svg{fill:currentColor;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%)}.cdk-high-contrast-active .mat-mdc-select-arrow svg{fill:CanvasText}.mat-mdc-select-disabled .cdk-high-contrast-active .mat-mdc-select-arrow svg{fill:GrayText}div.mat-mdc-select-panel{width:100%;max-height:275px;outline:0;overflow:auto;padding:8px 0;border-radius:4px;box-sizing:border-box;position:static;background-color:var(--mat-select-panel-background-color)}.cdk-high-contrast-active div.mat-mdc-select-panel{outline:solid 1px}.cdk-overlay-pane:not(.mat-mdc-select-panel-above) div.mat-mdc-select-panel{border-top-left-radius:0;border-top-right-radius:0;transform-origin:top center}.mat-mdc-select-panel-above div.mat-mdc-select-panel{border-bottom-left-radius:0;border-bottom-right-radius:0;transform-origin:bottom center}div.mat-mdc-select-panel .mat-mdc-option{--mdc-list-list-item-container-color: var(--mat-select-panel-background-color)}.mat-mdc-select-placeholder{transition:color 400ms 133.3333333333ms cubic-bezier(0.25, 0.8, 0.25, 1);color:var(--mat-select-placeholder-text-color)}._mat-animation-noopable .mat-mdc-select-placeholder{transition:none}.mat-form-field-hide-placeholder .mat-mdc-select-placeholder{color:rgba(0,0,0,0);-webkit-text-fill-color:rgba(0,0,0,0);transition:none;display:block}.mat-mdc-form-field-type-mat-select:not(.mat-form-field-disabled) .mat-mdc-text-field-wrapper{cursor:pointer}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-fill .mat-mdc-floating-label{max-width:calc(100% - 18px)}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-fill .mdc-floating-label--float-above{max-width:calc(100%/0.75 - 24px)}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-outline .mdc-notched-outline__notch{max-width:calc(100% - 60px)}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-outline .mdc-text-field--label-floating .mdc-notched-outline__notch{max-width:calc(100% - 24px)}.mat-mdc-select-min-line:empty::before{content:" ";white-space:pre;width:1px;display:inline-block;visibility:hidden}.mat-form-field-appearance-fill .mat-mdc-select-arrow-wrapper{transform:var(--mat-select-arrow-transform)}'], dependencies: [{ kind: "directive", type: CdkOverlayOrigin, selector: "[cdk-overlay-origin], [overlay-origin], [cdkOverlayOrigin]", exportAs: ["cdkOverlayOrigin"] }, { kind: "directive", type: CdkConnectedOverlay, selector: "[cdk-connected-overlay], [connected-overlay], [cdkConnectedOverlay]", inputs: ["cdkConnectedOverlayOrigin", "cdkConnectedOverlayPositions", "cdkConnectedOverlayPositionStrategy", "cdkConnectedOverlayOffsetX", "cdkConnectedOverlayOffsetY", "cdkConnectedOverlayWidth", "cdkConnectedOverlayHeight", "cdkConnectedOverlayMinWidth", "cdkConnectedOverlayMinHeight", "cdkConnectedOverlayBackdropClass", "cdkConnectedOverlayPanelClass", "cdkConnectedOverlayViewportMargin", "cdkConnectedOverlayScrollStrategy", "cdkConnectedOverlayOpen", "cdkConnectedOverlayDisableClose", "cdkConnectedOverlayTransformOriginOn", "cdkConnectedOverlayHasBackdrop", "cdkConnectedOverlayLockPosition", "cdkConnectedOverlayFlexibleDimensions", "cdkConnectedOverlayGrowAfterOpen", "cdkConnectedOverlayPush", "cdkConnectedOverlayDisposeOnNavigation"], outputs: ["backdropClick", "positionChange", "attach", "detach", "overlayKeydown", "overlayOutsideClick"], exportAs: ["cdkConnectedOverlay"] }, { kind: "directive", type: NgClass, selector: "[ngClass]", inputs: ["class", "ngClass"] }], animations: [matSelectAnimations.transformPanel], changeDetection: ChangeDetectionStrategy.OnPush, encapsulation: ViewEncapsulation$1.None });
var MatSelect = _MatSelect;
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: MatSelect, decorators: [{
  type: Component,
  args: [{ selector: "mat-select", exportAs: "matSelect", encapsulation: ViewEncapsulation$1.None, changeDetection: ChangeDetectionStrategy.OnPush, host: {
    "role": "combobox",
    "aria-autocomplete": "none",
    "aria-haspopup": "listbox",
    "class": "mat-mdc-select",
    "[attr.id]": "id",
    "[attr.tabindex]": "disabled ? -1 : tabIndex",
    "[attr.aria-controls]": 'panelOpen ? id + "-panel" : null',
    "[attr.aria-expanded]": "panelOpen",
    "[attr.aria-label]": "ariaLabel || null",
    "[attr.aria-required]": "required.toString()",
    "[attr.aria-disabled]": "disabled.toString()",
    "[attr.aria-invalid]": "errorState",
    "[attr.aria-activedescendant]": "_getAriaActiveDescendant()",
    "[class.mat-mdc-select-disabled]": "disabled",
    "[class.mat-mdc-select-invalid]": "errorState",
    "[class.mat-mdc-select-required]": "required",
    "[class.mat-mdc-select-empty]": "empty",
    "[class.mat-mdc-select-multiple]": "multiple",
    "(keydown)": "_handleKeydown($event)",
    "(focus)": "_onFocus()",
    "(blur)": "_onBlur()"
  }, animations: [matSelectAnimations.transformPanel], providers: [
    { provide: MatFormFieldControl, useExisting: MatSelect },
    { provide: MAT_OPTION_PARENT_COMPONENT, useExisting: MatSelect }
  ], standalone: true, imports: [CdkOverlayOrigin, CdkConnectedOverlay, NgClass], template: `<div cdk-overlay-origin
     class="mat-mdc-select-trigger"
     (click)="open()"
     #fallbackOverlayOrigin="cdkOverlayOrigin"
     #trigger>

  <div class="mat-mdc-select-value" [attr.id]="_valueId">
    @if (empty) {
      <span class="mat-mdc-select-placeholder mat-mdc-select-min-line">{{placeholder}}</span>
    } @else {
      <span class="mat-mdc-select-value-text">
        @if (customTrigger) {
          <ng-content select="mat-select-trigger"></ng-content>
        } @else {
          <span class="mat-mdc-select-min-line">{{triggerValue}}</span>
        }
      </span>
    }
  </div>

  <div class="mat-mdc-select-arrow-wrapper">
    <div class="mat-mdc-select-arrow">
      <!-- Use an inline SVG, because it works better than a CSS triangle in high contrast mode. -->
      <svg viewBox="0 0 24 24" width="24px" height="24px" focusable="false" aria-hidden="true">
        <path d="M7 10l5 5 5-5z"/>
      </svg>
    </div>
  </div>
</div>

<ng-template
  cdk-connected-overlay
  cdkConnectedOverlayLockPosition
  cdkConnectedOverlayHasBackdrop
  cdkConnectedOverlayBackdropClass="cdk-overlay-transparent-backdrop"
  [cdkConnectedOverlayPanelClass]="_overlayPanelClass"
  [cdkConnectedOverlayScrollStrategy]="_scrollStrategy"
  [cdkConnectedOverlayOrigin]="_preferredOverlayOrigin || fallbackOverlayOrigin"
  [cdkConnectedOverlayOpen]="panelOpen"
  [cdkConnectedOverlayPositions]="_positions"
  [cdkConnectedOverlayWidth]="_overlayWidth"
  (backdropClick)="close()"
  (attach)="_onAttached()"
  (detach)="close()">
  <div
    #panel
    role="listbox"
    tabindex="-1"
    class="mat-mdc-select-panel mdc-menu-surface mdc-menu-surface--open {{ _getPanelTheme() }}"
    [attr.id]="id + '-panel'"
    [attr.aria-multiselectable]="multiple"
    [attr.aria-label]="ariaLabel || null"
    [attr.aria-labelledby]="_getPanelAriaLabelledby()"
    [ngClass]="panelClass"
    [@transformPanel]="'showing'"
    (@transformPanel.done)="_panelDoneAnimatingStream.next($event.toState)"
    (keydown)="_handleKeydown($event)">
    <ng-content></ng-content>
  </div>
</ng-template>
`, styles: ['.mat-mdc-select{display:inline-block;width:100%;outline:none;-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;color:var(--mat-select-enabled-trigger-text-color);font-family:var(--mat-select-trigger-text-font);line-height:var(--mat-select-trigger-text-line-height);font-size:var(--mat-select-trigger-text-size);font-weight:var(--mat-select-trigger-text-weight);letter-spacing:var(--mat-select-trigger-text-tracking)}div.mat-mdc-select-panel{box-shadow:var(--mat-select-container-elevation-shadow)}.mat-mdc-select-disabled{color:var(--mat-select-disabled-trigger-text-color)}.mat-mdc-select-trigger{display:inline-flex;align-items:center;cursor:pointer;position:relative;box-sizing:border-box;width:100%}.mat-mdc-select-disabled .mat-mdc-select-trigger{-webkit-user-select:none;user-select:none;cursor:default}.mat-mdc-select-value{width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.mat-mdc-select-value-text{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mat-mdc-select-arrow-wrapper{height:24px;flex-shrink:0;display:inline-flex;align-items:center}.mat-form-field-appearance-fill .mdc-text-field--no-label .mat-mdc-select-arrow-wrapper{transform:none}.mat-mdc-form-field .mat-mdc-select.mat-mdc-select-invalid .mat-mdc-select-arrow,.mat-form-field-invalid:not(.mat-form-field-disabled) .mat-mdc-form-field-infix::after{color:var(--mat-select-invalid-arrow-color)}.mat-mdc-select-arrow{width:10px;height:5px;position:relative;color:var(--mat-select-enabled-arrow-color)}.mat-mdc-form-field.mat-focused .mat-mdc-select-arrow{color:var(--mat-select-focused-arrow-color)}.mat-mdc-form-field .mat-mdc-select.mat-mdc-select-disabled .mat-mdc-select-arrow{color:var(--mat-select-disabled-arrow-color)}.mat-mdc-select-arrow svg{fill:currentColor;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%)}.cdk-high-contrast-active .mat-mdc-select-arrow svg{fill:CanvasText}.mat-mdc-select-disabled .cdk-high-contrast-active .mat-mdc-select-arrow svg{fill:GrayText}div.mat-mdc-select-panel{width:100%;max-height:275px;outline:0;overflow:auto;padding:8px 0;border-radius:4px;box-sizing:border-box;position:static;background-color:var(--mat-select-panel-background-color)}.cdk-high-contrast-active div.mat-mdc-select-panel{outline:solid 1px}.cdk-overlay-pane:not(.mat-mdc-select-panel-above) div.mat-mdc-select-panel{border-top-left-radius:0;border-top-right-radius:0;transform-origin:top center}.mat-mdc-select-panel-above div.mat-mdc-select-panel{border-bottom-left-radius:0;border-bottom-right-radius:0;transform-origin:bottom center}div.mat-mdc-select-panel .mat-mdc-option{--mdc-list-list-item-container-color: var(--mat-select-panel-background-color)}.mat-mdc-select-placeholder{transition:color 400ms 133.3333333333ms cubic-bezier(0.25, 0.8, 0.25, 1);color:var(--mat-select-placeholder-text-color)}._mat-animation-noopable .mat-mdc-select-placeholder{transition:none}.mat-form-field-hide-placeholder .mat-mdc-select-placeholder{color:rgba(0,0,0,0);-webkit-text-fill-color:rgba(0,0,0,0);transition:none;display:block}.mat-mdc-form-field-type-mat-select:not(.mat-form-field-disabled) .mat-mdc-text-field-wrapper{cursor:pointer}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-fill .mat-mdc-floating-label{max-width:calc(100% - 18px)}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-fill .mdc-floating-label--float-above{max-width:calc(100%/0.75 - 24px)}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-outline .mdc-notched-outline__notch{max-width:calc(100% - 60px)}.mat-mdc-form-field-type-mat-select.mat-form-field-appearance-outline .mdc-text-field--label-floating .mdc-notched-outline__notch{max-width:calc(100% - 24px)}.mat-mdc-select-min-line:empty::before{content:" ";white-space:pre;width:1px;display:inline-block;visibility:hidden}.mat-form-field-appearance-fill .mat-mdc-select-arrow-wrapper{transform:var(--mat-select-arrow-transform)}'] }]
}], ctorParameters: () => [{ type: ViewportRuler }, { type: ChangeDetectorRef }, { type: NgZone }, { type: ErrorStateMatcher }, { type: ElementRef }, { type: Directionality, decorators: [{
  type: Optional
}] }, { type: NgForm, decorators: [{
  type: Optional
}] }, { type: FormGroupDirective, decorators: [{
  type: Optional
}] }, { type: MatFormField, decorators: [{
  type: Optional
}, {
  type: Inject,
  args: [MAT_FORM_FIELD]
}] }, { type: NgControl, decorators: [{
  type: Self
}, {
  type: Optional
}] }, { type: void 0, decorators: [{
  type: Attribute,
  args: ["tabindex"]
}] }, { type: void 0, decorators: [{
  type: Inject,
  args: [MAT_SELECT_SCROLL_STRATEGY]
}] }, { type: LiveAnnouncer }, { type: void 0, decorators: [{
  type: Optional
}, {
  type: Inject,
  args: [MAT_SELECT_CONFIG]
}] }], propDecorators: { options: [{
  type: ContentChildren,
  args: [MatOption, { descendants: true }]
}], optionGroups: [{
  type: ContentChildren,
  args: [MAT_OPTGROUP, { descendants: true }]
}], customTrigger: [{
  type: ContentChild,
  args: [MAT_SELECT_TRIGGER]
}], userAriaDescribedBy: [{
  type: Input,
  args: ["aria-describedby"]
}], trigger: [{
  type: ViewChild,
  args: ["trigger"]
}], panel: [{
  type: ViewChild,
  args: ["panel"]
}], _overlayDir: [{
  type: ViewChild,
  args: [CdkConnectedOverlay]
}], panelClass: [{
  type: Input
}], disabled: [{
  type: Input,
  args: [{ transform: booleanAttribute }]
}], disableRipple: [{
  type: Input,
  args: [{ transform: booleanAttribute }]
}], tabIndex: [{
  type: Input,
  args: [{
    transform: (value) => value == null ? 0 : numberAttribute(value)
  }]
}], hideSingleSelectionIndicator: [{
  type: Input,
  args: [{ transform: booleanAttribute }]
}], placeholder: [{
  type: Input
}], required: [{
  type: Input,
  args: [{ transform: booleanAttribute }]
}], multiple: [{
  type: Input,
  args: [{ transform: booleanAttribute }]
}], disableOptionCentering: [{
  type: Input,
  args: [{ transform: booleanAttribute }]
}], compareWith: [{
  type: Input
}], value: [{
  type: Input
}], ariaLabel: [{
  type: Input,
  args: ["aria-label"]
}], ariaLabelledby: [{
  type: Input,
  args: ["aria-labelledby"]
}], errorStateMatcher: [{
  type: Input
}], typeaheadDebounceInterval: [{
  type: Input,
  args: [{ transform: numberAttribute }]
}], sortComparator: [{
  type: Input
}], id: [{
  type: Input
}], panelWidth: [{
  type: Input
}], openedChange: [{
  type: Output
}], _openedStream: [{
  type: Output,
  args: ["opened"]
}], _closedStream: [{
  type: Output,
  args: ["closed"]
}], selectionChange: [{
  type: Output
}], valueChange: [{
  type: Output
}] } });
var _MatSelectTrigger = class _MatSelectTrigger {
};
_MatSelectTrigger.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: _MatSelectTrigger, deps: [], target: FactoryTarget.Directive });
_MatSelectTrigger.\u0275dir = \u0275\u0275ngDeclareDirective({ minVersion: "14.0.0", version: "17.2.0", type: _MatSelectTrigger, isStandalone: true, selector: "mat-select-trigger", providers: [{ provide: MAT_SELECT_TRIGGER, useExisting: _MatSelectTrigger }], ngImport: core_exports });
var MatSelectTrigger = _MatSelectTrigger;
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: MatSelectTrigger, decorators: [{
  type: Directive,
  args: [{
    selector: "mat-select-trigger",
    providers: [{ provide: MAT_SELECT_TRIGGER, useExisting: MatSelectTrigger }],
    standalone: true
  }]
}] });
var _MatSelectModule = class _MatSelectModule {
};
_MatSelectModule.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: _MatSelectModule, deps: [], target: FactoryTarget.NgModule });
_MatSelectModule.\u0275mod = \u0275\u0275ngDeclareNgModule({ minVersion: "14.0.0", version: "17.2.0", ngImport: core_exports, type: _MatSelectModule, imports: [
  CommonModule,
  OverlayModule,
  MatOptionModule,
  MatCommonModule,
  MatSelect,
  MatSelectTrigger
], exports: [
  CdkScrollableModule,
  MatFormFieldModule,
  MatSelect,
  MatSelectTrigger,
  MatOptionModule,
  MatCommonModule
] });
_MatSelectModule.\u0275inj = \u0275\u0275ngDeclareInjector({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: _MatSelectModule, providers: [MAT_SELECT_SCROLL_STRATEGY_PROVIDER], imports: [
  CommonModule,
  OverlayModule,
  MatOptionModule,
  MatCommonModule,
  CdkScrollableModule,
  MatFormFieldModule,
  MatOptionModule,
  MatCommonModule
] });
var MatSelectModule = _MatSelectModule;
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "17.2.0", ngImport: core_exports, type: MatSelectModule, decorators: [{
  type: NgModule,
  args: [{
    imports: [
      CommonModule,
      OverlayModule,
      MatOptionModule,
      MatCommonModule,
      MatSelect,
      MatSelectTrigger
    ],
    exports: [
      CdkScrollableModule,
      MatFormFieldModule,
      MatSelect,
      MatSelectTrigger,
      MatOptionModule,
      MatCommonModule
    ],
    providers: [MAT_SELECT_SCROLL_STRATEGY_PROVIDER]
  }]
}] });

// projects/aimmo-design-system/aim-select/src/aim-select-animations.ts
var aimSelectAnimations = {
  aimTransformPanelWrap: trigger("aimTransformPanelWrap", [
    transition("* => void", query("@aimTransformPanel", [animateChild()], { optional: true }))
  ]),
  aimTransformPanel: trigger("aimTransformPanel", [
    state("void", style({
      opacity: 0,
      transform: "scale(1, 0.8)"
    })),
    transition("void => showing", animate("120ms cubic-bezier(0, 0, 0.2, 1)", style({
      opacity: 1,
      transform: "scale(1, 1)"
    }))),
    transition("* => void", animate("100ms linear", style({ opacity: 0 })))
  ])
};

// projects/aimmo-design-system/aim-select/src/aim-select.component.ts
var nextUniqueId2 = 0;
var AIM_SELECT_SCROLL_STRATEGY = new InjectionToken("aim-select-scroll-strategy");
function AIM_SELECT_SCROLL_STRATEGY_PROVIDER_FACTORY(overlay) {
  return () => overlay.scrollStrategies.reposition();
}
var AIM_SELECT_CONFIG = new InjectionToken("AIM_SELECT_CONFIG");
var AIM_SELECT_SCROLL_STRATEGY_PROVIDER = {
  provide: AIM_SELECT_SCROLL_STRATEGY,
  deps: [Overlay],
  useFactory: AIM_SELECT_SCROLL_STRATEGY_PROVIDER_FACTORY
};
var AimSelectChange = class {
  constructor(source, value) {
    this.source = source;
    this.value = value;
  }
};
var _a;
var AimSelectComponent = (_a = class extends MatSelect {
  constructor(overlayOrigin, selectContext, document, viewportRuler, changeDetectorRef, ngZone, defaultErrorStateMatcher, elementRef, dir, parentForm, parentFormGroup, parentFormLayout, ngCtrl, tabIdx, scrollStrategyFactory, liveAnnouncer, defaultOptions) {
    super(viewportRuler, changeDetectorRef, ngZone, defaultErrorStateMatcher, elementRef, dir, parentForm, parentFormGroup, void 0, ngCtrl, tabIdx, scrollStrategyFactory, liveAnnouncer, defaultOptions);
    this.overlayOrigin = overlayOrigin;
    this.selectContext = selectContext;
    this.document = document;
    this.viewportRuler = viewportRuler;
    this.changeDetectorRef = changeDetectorRef;
    this.ngZone = ngZone;
    this.defaultErrorStateMatcher = defaultErrorStateMatcher;
    this.elementRef = elementRef;
    this.dir = dir;
    this.parentForm = parentForm;
    this.parentFormGroup = parentFormGroup;
    this.parentFormLayout = parentFormLayout;
    this.ngCtrl = ngCtrl;
    this.tabIdx = tabIdx;
    this.scrollStrategyFactory = scrollStrategyFactory;
    this.liveAnnouncer = liveAnnouncer;
    this.defaultOptions = defaultOptions;
    this.controlType = "aim-select";
    this.selectSizeType = AimSelectFieldSize;
    this.overlayOffset = { x: 0, y: 0 };
    this.optionSelectionChanges = this.optionSelectionChangesAction();
    this.triggerAriaLabelledby = null;
    this._positions = [
      { originX: "start", originY: "bottom", overlayX: "start", overlayY: "top" },
      { originX: "start", originY: "top", overlayX: "start", overlayY: "bottom" },
      { originX: "end", originY: "bottom", overlayX: "end", overlayY: "top" }
    ];
    this._onChange = (value) => {
      return new AimSelectChange(this, value);
    };
    this.responsivePanel = false;
    this.ariaLabelledby = "";
    this.viewportChangeThrottleTime = 100;
    this.isSizeChanged = false;
    this.selectHeaderIcon = "";
    this.selectSize = this.selectSizeType.fill;
    this.parentContext = AimSelectContext.normal;
    this.fixedOptionHeight = null;
    this.updateSource = new Subject();
    this.initializeStatus();
  }
  get size() {
    return this.selectSize;
  }
  set size(value) {
    if (value !== this.selectSize) {
      this.selectSize = value;
      this.stateChanges.next(void 0);
    }
  }
  get headerIcon() {
    return this.selectHeaderIcon;
  }
  set headerIcon(value) {
    this.selectHeaderIcon = value;
    this.stateChanges.next(void 0);
  }
  get selectFieldWidth() {
    return this.context !== AimSelectContext.normal ? null : AimSelectFieldWidth[this.size];
  }
  get isTableContext() {
    return this.context === AimSelectContext.table;
  }
  get hasHeaderIcon() {
    return !!this.headerIcon;
  }
  get triggerIcon() {
    return this.panelOpen ? "chevron-up" : "chevron-down";
  }
  // TODO: 테마 변경이 필요한 경우 구현.
  get panelTheme() {
    return "";
  }
  get context() {
    return this.parentContext;
  }
  get optionHeight() {
    return this.fixedOptionHeight || this.triggerRect?.height;
  }
  /** TODO: 뷰포트에 따라 패널 크기 조정 필요하면 구현, 변경 중 이벤트 다량 발생 처리 필요할 수도... */
  get viewportChangeAction$() {
    return this.viewportRuler.change(this.viewportChangeThrottleTime).pipe(filter(() => this.panelOpen), tap(() => {
      this.triggerRect = this.getTriggerRect();
      this.changeDetectorRef.markForCheck();
      this.stateChanges.next(void 0);
    }));
  }
  get updateAction$() {
    return merge(this._openedStream, this.updateSource).pipe(tap(() => this._scrollOptionIntoView(this._keyManager.activeItemIndex || 0)));
  }
  ngOnInit() {
    super.ngOnInit();
    this.initTriggerAriaLabelledby();
    forkJoin([
      this.viewportChangeAction$,
      this.updateAction$
    ]).pipe(takeUntil(this._destroy)).subscribe();
  }
  ngOnChanges(changes) {
    super.ngOnChanges(changes);
    if (changes.size) {
      this.isSizeChanged = changes.size.previousValue !== changes.size.currentValue;
    }
  }
  ngAfterContentInit() {
    super.ngAfterContentInit();
    if (!!this.customPanelTrigger) {
      this.fixedOptionHeight = SelectOptionHeight[this.context];
    }
  }
  ngAfterViewChecked() {
    if (this.panelOpen && this.isSizeChanged) {
      this.isSizeChanged = false;
      this.triggerRect = this.getTriggerRect();
      this.changeDetectorRef.detectChanges();
      this.updateSource.next();
    } else {
      this.isSizeChanged = false;
    }
    if (!!this.customPanelTrigger) {
      const size = this.size !== AimSelectFieldSize.fill ? this.size : AimSelectFieldSize.small;
      this.panelWidth = parseInt(AimSelectFieldWidth[size], 10);
    } else {
      this.panelWidth = this.triggerRect?.width;
    }
  }
  // TODO: 수정 이유 이력 추적 중 by Rex
  //  https://app.asana.com/0/1179494858925986/1203831553868817/f
  initTriggerAriaLabelledby() {
    this.triggerAriaLabelledby = this.ariaLabel ? null : `${this.parentFormLayout?.labelId || ""} ${this._valueId} ${this.ariaLabelledby}`.trim();
    this.changeDetectorRef.detectChanges();
  }
  panelAriaLabelledby() {
    if (this.ariaLabel) {
      return null;
    }
    const labelId = this.parentFormLayout?.labelId;
    return this.ariaLabelledby ? `${labelId} ${this.ariaLabelledby}`.trim() : labelId;
  }
  open() {
    this.triggerRect = this.getTriggerRect();
    super.open();
    if (this.empty) {
      this._keyManager.setActiveItem(-1);
    }
  }
  close() {
    super.close();
  }
  _scrollOptionIntoView(index) {
    const option = this.options.toArray()[index];
    if (!option) {
      return void 0;
    }
    const panel = this.panel.nativeElement;
    const labelCount = _countGroupLabelsBeforeOption(index, this.options, this.optionGroups);
    const optionHeight = this.optionHeight;
    if (index === 0 && labelCount === 1) {
      panel.scrollTop = 0;
    } else {
      panel.scrollTop = _getOptionScrollPosition((index + labelCount) * optionHeight, optionHeight, panel.scrollTop, panel.offsetHeight);
    }
  }
  initializeStatus() {
    this.id = `aim-select-${nextUniqueId2++}`;
    this._valueId = `aim-select-value-${nextUniqueId2++}`;
    this.disableOptionCentering = true;
    this.disableRipple = true;
    this.parentContext = this.selectContext?.type || AimSelectContext.normal;
  }
  getTriggerRect() {
    return this.elementRef.nativeElement.getBoundingClientRect();
  }
  optionSelectionChangesAction() {
    return defer(() => {
      const options = this.options;
      if (!isNil_default(options) && options.length !== 0) {
        return options.changes.pipe(startWith(options), switchMap(() => merge(...options.map((option) => option.onSelectionChange))), takeUntil(options.changes));
      }
      return this.ngZone.onStable.pipe(take(1), switchMap(() => this.optionSelectionChanges));
    });
  }
}, _a.ctorParameters = () => [
  { type: CdkOverlayOrigin },
  { type: AimSelectContext, decorators: [{ type: Optional }, { type: Self }, { type: Inject, args: [AIM_SELECT_CONTEXT] }] },
  { type: void 0, decorators: [{ type: Optional }, { type: Inject, args: [DOCUMENT] }] },
  { type: ViewportRuler },
  { type: ChangeDetectorRef },
  { type: NgZone },
  { type: ErrorStateMatcher },
  { type: ElementRef },
  { type: Directionality, decorators: [{ type: Optional }] },
  { type: NgForm, decorators: [{ type: Optional }] },
  { type: FormGroupDirective, decorators: [{ type: Optional }] },
  { type: AimFormLayoutComponent, decorators: [{ type: Optional }, { type: Inject, args: [AIM_FORM_LAYOUT] }] },
  { type: NgControl, decorators: [{ type: Self }, { type: Optional }] },
  { type: String, decorators: [{ type: Attribute, args: ["tabindex"] }] },
  { type: Function, decorators: [{ type: Inject, args: [AIM_SELECT_SCROLL_STRATEGY] }] },
  { type: LiveAnnouncer },
  { type: void 0, decorators: [{ type: Optional }, { type: Inject, args: [AIM_SELECT_CONFIG] }] }
], _a.propDecorators = {
  responsivePanel: [{ type: Input }],
  customPanelClass: [{ type: Input }],
  ariaLabelledby: [{ type: Input, args: ["aria-labelledby"] }],
  customPanelTrigger: [{ type: ContentChild, args: [AIM_SELECT_PANEL_TRIGGER] }],
  customTrigger: [{ type: ContentChild, args: [AIM_SELECT_TRIGGER] }],
  options: [{ type: ContentChildren, args: [AimOptionComponent, { descendants: true }] }],
  optionGroups: [{ type: ContentChildren, args: [AimOptgroupComponent, { descendants: true }] }],
  size: [{ type: Input }],
  headerIcon: [{ type: Input }],
  selectFieldWidth: [{ type: HostBinding, args: ["style.--select-field-width"] }]
}, _a);
AimSelectComponent = __decorate([
  Component({
    selector: "aim-select",
    template: aim_select_component_default,
    exportAs: "aimSelect",
    inputs: ["disabled", "disableRipple", "tabIndex"],
    hostDirectives: [CdkOverlayOrigin],
    changeDetection: ChangeDetectionStrategy.OnPush,
    host: {
      role: "combobox",
      "aria-autocomplete": "none",
      "aria-haspopup": "listbox",
      class: "aim-select aim-select-trigger",
      "[attr.id]": "id",
      "[attr.tabindex]": "tabIndex",
      "[attr.aria-owns]": 'panelOpen ? id + "-panel" : null',
      "[attr.aria-controls]": 'panelOpen ? id + "-panel" : null',
      "[attr.aria-expanded]": "panelOpen",
      "[attr.aria-label]": "ariaLabel || null",
      "[attr.aria-labelledby]": "triggerAriaLabelledby",
      "[attr.aria-required]": "required.toString()",
      "[attr.aria-disabled]": "disabled.toString()",
      "[attr.aria-invalid]": "errorState",
      "[attr.aria-activedescendant]": "_getAriaActiveDescendant()",
      "[class.aim-select--disabled]": "disabled",
      "[class.aim-select--active]": "panelOpen",
      "[class.aim-select--invalid]": "errorState",
      "[class.aim-select--required]": "required",
      "[class.aim-select--empty]": "empty",
      "[class.aim-select--multiple]": "multiple",
      "[class.table]": "isTableContext",
      "[class.fit-content]": "!!customPanelTrigger",
      "(keydown)": "_handleKeydown($event)",
      "(click)": "toggle()",
      "(focus)": "_onFocus()",
      "(blur)": "_onBlur()"
    },
    animations: [aimSelectAnimations.aimTransformPanel],
    providers: [
      { provide: AimFormLayoutControl, useExisting: AimSelectComponent },
      { provide: AIM_OPTION_PARENT_COMPONENT, useExisting: AimSelectComponent }
    ],
    styles: [aim_select_component_default2]
  })
], AimSelectComponent);

// projects/aimmo-design-system/aim-select/src/aim-select.module.ts
var AimSelectModule = class AimSelectModule2 {
};
AimSelectModule = __decorate([
  NgModule({
    declarations: [
      AimSelectComponent,
      AimSelectTrigger,
      AimSelectPanelTrigger
    ],
    imports: [
      AimIconComponent,
      OverlayModule,
      CdkConnectedOverlay,
      NgClass,
      NgIf
    ],
    exports: [
      AimSelectComponent,
      AimSelectTrigger,
      AimSelectPanelTrigger,
      AimOptionModule
    ],
    providers: [AIM_SELECT_SCROLL_STRATEGY_PROVIDER]
  })
], AimSelectModule);

// projects/static-embedding-viewer/src/app/app.route.paths.ts
var route = {
  home: {
    name: "home",
    path: "",
    fullPath: "/"
  },
  dataset: {
    name: "dataset",
    path: `dataset/:datasetId`,
    fullPath: DATASET_PATH
  }
};
function DATASET_PATH(datasetId) {
  return `/dataset/${datasetId}`;
}

// projects/aimmo-i18n/src/model.ts
var Lang;
(function(Lang2) {
  Lang2["KO"] = "ko";
  Lang2["EN"] = "en";
  Lang2["VI"] = "vi";
  Lang2["JA"] = "ja";
})(Lang || (Lang = {}));
var LANGUAGE_CODES = [
  Lang.KO,
  Lang.EN,
  Lang.VI,
  Lang.JA
];
function getLanguageCode(code) {
  return LANGUAGE_CODES.find((languageCode2) => isEqual_default(code, languageCode2));
}
var SupportLanguages = {
  admin: [Lang.KO, Lang.EN],
  dassDatasetViewer: [Lang.KO, Lang.EN],
  external: LANGUAGE_CODES,
  labelers: LANGUAGE_CODES,
  labelersCsCenter: [Lang.KO, Lang.EN, Lang.VI],
  labelersInhouse: [Lang.KO, Lang.EN, Lang.VI],
  gtaas: LANGUAGE_CODES,
  aimmoCore: [Lang.KO, Lang.EN]
};
var I18N_GUARD_CONFIG = new InjectionToken("I18nGuardConfig");

// node_modules/ngforage/fesm2020/ngforage.mjs
var lf = __toESM(require_localforage(), 1);
var CachedItemImpl = class {
  constructor(data, expiryTime) {
    this.data = data;
    this.expires = new Date(typeof expiryTime === "number" ? expiryTime : 0);
    this.hasData = data != null;
  }
  get expired() {
    return this.expiresIn === 0;
  }
  get expiresIn() {
    return Math.max(0, this.expires.getTime() - Date.now());
  }
  toJSON() {
    return {
      data: this.data,
      expired: this.expired,
      expires: this.expires,
      expiresIn: this.expiresIn,
      hasData: this.hasData
    };
  }
  toString() {
    return JSON.stringify(this.toJSON());
  }
};
var localForage = "defineDriver" in lf ? lf : lf.default;
var Driver;
(function(Driver2) {
  Driver2[Driver2["INDEXED_DB"] = localForage.INDEXEDDB] = "INDEXED_DB";
  Driver2[Driver2["LOCAL_STORAGE"] = localForage.LOCALSTORAGE] = "LOCAL_STORAGE";
  Driver2[Driver2["WEB_SQL"] = localForage.WEBSQL] = "WEB_SQL";
})(Driver || (Driver = {}));
for (const d of [localForage.INDEXEDDB, localForage.LOCALSTORAGE, localForage.WEBSQL]) {
  delete Driver[d];
}
Object.freeze(Driver);
var DEFAULT_CONFIG = new InjectionToken("Default NgForage config");
var $defaultConfig = Symbol("Default Config");
var NgForageConfig = class {
  constructor(conf) {
    this[$defaultConfig] = {
      cacheTime: 3e5,
      description: "",
      driver: [Driver.INDEXED_DB, Driver.WEB_SQL, Driver.LOCAL_STORAGE],
      name: "ngForage",
      size: 4980736,
      storeName: "ng_forage",
      version: 1
    };
    if (conf) {
      this.configure(conf);
    }
  }
  /**
   * Cache time in milliseconds
   * @default 300000
   */
  get cacheTime() {
    return this[$defaultConfig].cacheTime;
  }
  set cacheTime(t) {
    this[$defaultConfig].cacheTime = t;
  }
  /**
   * Get the compiled configuration
   */
  get config() {
    return {
      cacheTime: this.cacheTime,
      description: this.description,
      driver: this.driver,
      name: this.name,
      size: this.size,
      storeName: this.storeName,
      version: this.version
    };
  }
  /**
   * A description of the database, essentially for developer usage.
   * @default
   */
  get description() {
    return this[$defaultConfig].description;
  }
  set description(v) {
    this[$defaultConfig].description = v;
  }
  /**
   * The preferred driver(s) to use.
   */
  get driver() {
    const d = this[$defaultConfig].driver;
    if (!d) {
      return [];
    } else if (Array.isArray(d)) {
      return d.slice();
    }
    return d;
  }
  set driver(v) {
    this[$defaultConfig].driver = v;
  }
  /**
   * The name of the database. May appear during storage limit prompts. Useful to use the name of your app here.
   * In localStorage, this is used as a key prefix for all keys stored in localStorage.
   * @default ngForage
   */
  get name() {
    return this[$defaultConfig].name;
  }
  set name(v) {
    this[$defaultConfig].name = v;
  }
  /**
   * The size of the database in bytes. Used only in WebSQL for now.
   * @default 4980736
   */
  get size() {
    return this[$defaultConfig].size;
  }
  set size(v) {
    this[$defaultConfig].size = v;
  }
  /**
   * The name of the datastore.
   * In IndexedDB this is the dataStore,
   * in WebSQL this is the name of the key/value table in the database.
   * Must be alphanumeric, with underscores.
   * Any non-alphanumeric characters will be converted to underscores.
   * @default ng_forage
   */
  get storeName() {
    return this[$defaultConfig].storeName;
  }
  set storeName(v) {
    this[$defaultConfig].storeName = v;
  }
  /**
   * The version of your database. May be used for upgrades in the future; currently unused.
   * @default 1.0
   */
  get version() {
    return this[$defaultConfig].version;
  }
  set version(v) {
    this[$defaultConfig].version = v;
  }
  /**
   * Bulk-set configuration options
   * @param opts The configuration
   */
  configure(opts) {
    const resolved = __spreadValues({}, opts);
    if (Array.isArray(resolved?.driver)) {
      resolved.driver = resolved.driver.slice();
    }
    Object.assign(this[$defaultConfig], resolved);
    return this;
  }
  /**
   * Define a driver
   *
   * You’ll want to make sure you accept a callback argument and that you pass the same arguments to callbacks as the
   * default drivers do. You’ll also want to resolve or reject promises.
   * Check any of the {@link https://github.com/mozilla/localForage/tree/master/src/drivers default drivers}
   * for an idea of how to implement your own, custom driver.
   * @param spec Driver spec
   */
  defineDriver(spec) {
    return __async(this, null, function* () {
      return yield localForage.defineDriver(spec);
    });
  }
  /** @internal */
  toJSON() {
    return this.config;
  }
  toString() {
    return JSON.stringify(this.toJSON());
  }
};
NgForageConfig.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForageConfig, deps: [{ token: DEFAULT_CONFIG, optional: true }], target: FactoryTarget.Injectable });
NgForageConfig.\u0275prov = \u0275\u0275ngDeclareInjectable({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForageConfig, providedIn: "root" });
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForageConfig, decorators: [{
  type: Injectable,
  args: [{ providedIn: "root" }]
}], ctorParameters: function() {
  return [{ type: void 0, decorators: [{
    type: Optional
  }, {
    type: Inject,
    args: [DEFAULT_CONFIG]
  }] }];
} });
var stores = /* @__PURE__ */ new Map();
function getDriverString(driver) {
  if (!driver) {
    return "";
  } else if (Array.isArray(driver)) {
    return driver.slice().sort().join(",");
  } else {
    return driver;
  }
}
function getHash(cfg) {
  return [
    getDriverString(cfg.driver),
    cfg.name,
    cfg.size,
    cfg.storeName,
    cfg.version,
    cfg.description,
    cfg.cacheTime
  ].join("|");
}
var conf$$1 = Symbol("Config");
var InstanceFactory = class {
  constructor(conf) {
    this[conf$$1] = conf;
  }
  getInstance(cfg) {
    const resolvedCfg = __spreadValues(__spreadValues({}, this[conf$$1].config), cfg);
    const hash = getHash(resolvedCfg);
    const existing = stores.get(hash);
    if (existing) {
      return existing;
    }
    const nu = localForage.createInstance(resolvedCfg);
    const origDropInstance = nu.dropInstance;
    nu.dropInstance = function() {
      stores.delete(hash);
      return origDropInstance.apply(this, arguments);
    };
    stores.set(hash, nu);
    return nu;
  }
};
InstanceFactory.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: InstanceFactory, deps: [{ token: NgForageConfig }], target: FactoryTarget.Injectable });
InstanceFactory.\u0275prov = \u0275\u0275ngDeclareInjectable({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: InstanceFactory, providedIn: "root" });
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: InstanceFactory, decorators: [{
  type: Injectable,
  args: [{ providedIn: "root" }]
}], ctorParameters: function() {
  return [{ type: NgForageConfig }];
} });
var store$ = Symbol("Store");
var BaseConfigurableImpl = class {
  /** @internal */
  constructor(config, instanceFactory) {
    this.config = {};
    this.storeNeedsRecalc = true;
    this.baseConfig = config;
    this.fact = instanceFactory;
  }
  /**
   * A description of the database, essentially for developer usage.
   * @default ""
   */
  get description() {
    return this.config.description || this.baseConfig.description;
  }
  set description(v) {
    this.config.description = v;
    this.storeNeedsRecalc = true;
  }
  /**
   * The preferred driver(s) to use.
   * @default IndexedDB, WebSQL and localStorage
   */
  get driver() {
    return this.config.driver ?? this.baseConfig.driver;
  }
  set driver(v) {
    this.config.driver = v;
    this.storeNeedsRecalc = true;
  }
  /**
   * The name of the database. May appear during storage limit prompts. Useful to use the name of your app here.
   * In localStorage, this is used as a key prefix for all keys stored in localStorage.
   * @default ngForage
   */
  get name() {
    return this.config.name || this.baseConfig.name;
  }
  set name(v) {
    this.config.name = v;
    this.storeNeedsRecalc = true;
  }
  /**
   * The size of the database in bytes. Used only in WebSQL for now.
   * @default 4980736
   */
  get size() {
    return this.config.size ?? this.baseConfig.size;
  }
  set size(v) {
    this.config.size = v;
    this.storeNeedsRecalc = true;
  }
  /**
   * The name of the datastore.
   * In IndexedDB this is the dataStore,
   * in WebSQL this is the name of the key/value table in the database.
   * Must be alphanumeric, with underscores.
   * Any non-alphanumeric characters will be converted to underscores.
   * @default ng_forage
   */
  get storeName() {
    return this.config.storeName ?? this.baseConfig.storeName;
  }
  set storeName(v) {
    this.config.storeName = v;
    this.storeNeedsRecalc = true;
  }
  /**
   * The version of your database. May be used for upgrades in the future; currently unused.
   * @default 1.0
   */
  get version() {
    return this.config?.version ?? this.baseConfig.version;
  }
  set version(v) {
    this.config.version = v;
    this.storeNeedsRecalc = true;
  }
  /** @internal */
  get finalConfig() {
    return __spreadValues(__spreadValues({}, this.baseConfig.config), this.config);
  }
  /** @internal */
  get store() {
    if (this.storeNeedsRecalc || !this[store$]) {
      this[store$] = this.fact.getInstance(this.finalConfig);
      this.storeNeedsRecalc = false;
    }
    return this[store$];
  }
  /**
   * Bulk-set configuration options
   * @param opts The configuration
   */
  configure(opts) {
    opts = opts || {};
    if (Array.isArray(opts.driver)) {
      opts.driver = opts.driver.slice();
    }
    Object.assign(this.config, opts);
    this.storeNeedsRecalc = true;
    return this;
  }
  toJSON() {
    return {
      description: this.description,
      driver: this.driver,
      name: this.name,
      size: this.size,
      storeName: this.storeName,
      version: this.version
    };
  }
  toString() {
    return JSON.stringify(this.toJSON());
  }
};
BaseConfigurableImpl.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: BaseConfigurableImpl, deps: [{ token: NgForageConfig }, { token: InstanceFactory }], target: FactoryTarget.Injectable });
BaseConfigurableImpl.\u0275prov = \u0275\u0275ngDeclareInjectable({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: BaseConfigurableImpl });
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: BaseConfigurableImpl, decorators: [{
  type: Injectable
}], ctorParameters: function() {
  return [{ type: NgForageConfig, decorators: [{
    type: Inject,
    args: [NgForageConfig]
  }] }, { type: InstanceFactory, decorators: [{
    type: Inject,
    args: [InstanceFactory]
  }] }];
} });
var NgForage = class _NgForage extends BaseConfigurableImpl {
  /**
   * Returns the name of the driver being used, or null if none can be used.
   */
  get activeDriver() {
    return this.store.driver();
  }
  /**
   * When invoked with no arguments, it drops the “store” of the current instance. When invoked with an object
   * specifying both name and storeName properties, it drops the specified “store”. When invoked with an object
   * specifying only a name property, it drops the specified “database” (and all its stores).
   */
  dropInstance(cfg) {
    return __async(this, null, function* () {
      return yield cfg ? this.store.dropInstance(cfg) : this.store.dropInstance();
    });
  }
  /**
   * Removes every key from the database, returning it to a blank slate.
   *
   * clear() will remove <b>every item in the offline store</b>. Use this method with caution.
   */
  clear() {
    return __async(this, null, function* () {
      return yield this.store.clear();
    });
  }
  /**
   * Make a clone of the instance
   * @param config Optional configuration
   */
  clone(config) {
    const inst = new _NgForage(this.baseConfig, this.fact);
    inst.configure(__spreadValues(__spreadValues({}, this.finalConfig), config));
    return inst;
  }
  /**
   * Gets an item from the storage library.
   * If the key does not exist, getItem() will return null.
   * @param key Data key
   */
  getItem(key) {
    return __async(this, null, function* () {
      return yield this.store.getItem(key);
    });
  }
  /**
   * Iterate over all value/key pairs in datastore.
   * <i>iteratee</i> is called once for each pair, with the following arguments:
   * <ol>
   *   <li>Value</li>
   *   <li>Key</li>
   *   <li>iterationNumber - one-based number</li>
   * </ol>
   * iterate() supports early exit by returning non undefined value inside iteratorCallback callback.
   * @param iteratee
   */
  iterate(iteratee) {
    return __async(this, null, function* () {
      return yield this.store.iterate(iteratee);
    });
  }
  /**
   * Get the name of a key based on its ID.
   * @param index
   */
  key(index) {
    return __async(this, null, function* () {
      return yield this.store.key(index);
    });
  }
  /**
   * Get the list of all keys in the datastore.
   */
  keys() {
    return __async(this, null, function* () {
      return yield this.store.keys();
    });
  }
  /**
   * Gets the number of keys in the offline store (i.e. its “length”).
   */
  length() {
    return __async(this, null, function* () {
      return yield this.store.length();
    });
  }
  /**
   * Even though localForage queues up all of its data API method calls,
   * ready() provides a way to determine whether the asynchronous driver initialization process has finished.
   * That’s useful in cases like when we want to know which driver localForage has settled down using.
   */
  ready() {
    return __async(this, null, function* () {
      return yield this.store.ready();
    });
  }
  /**
   * Removes the value of a key from the offline store.
   * @param key Data key
   */
  removeItem(key) {
    return __async(this, null, function* () {
      return yield this.store.removeItem(key);
    });
  }
  /**
   * Saves data to an offline store. You can store the following types of JavaScript objects:
   * <ul>
   *  <li>Array</li>
   *  <li>ArrayBuffer</li>
   *  <li>Blob</li>
   *  <li>Float32Array</li>
   *  <li>Float64Array</li>
   *  <li>Int8Array</li>
   *  <li>Int16Array</li>
   *  <li>Int32Array</li>
   *  <li>Number</li>
   *  <li>Object</li>
   *  <li>Uint8Array</li>
   *  <li>Uint8ClampedArray</li>
   *  <li>Uint16Array</li>
   *  <li>Uint32Array</li>
   *  <li>String</li>
   * </ul>
   * @param key Data key
   * @param data Data
   */
  setItem(key, data) {
    return __async(this, null, function* () {
      return yield this.store.setItem(key, data);
    });
  }
  /**
   * Check whether the given driver is supported/registered.
   * @param driver Driver name
   */
  supports(driver) {
    return this.store.supports(driver);
  }
};
NgForage.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForage, deps: null, target: FactoryTarget.Injectable });
NgForage.\u0275prov = \u0275\u0275ngDeclareInjectable({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForage, providedIn: "root" });
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForage, decorators: [{
  type: Injectable,
  args: [{ providedIn: "root" }]
}] });
function calculateCacheKeys(mainKey) {
  return {
    data: `${mainKey}_data`,
    expiry: `${mainKey}_expiry`
  };
}
var NgForageCache = class _NgForageCache extends NgForage {
  /**
   * Cache time in milliseconds
   * @default 300000
   */
  get cacheTime() {
    return this.config.cacheTime ?? this.baseConfig.cacheTime;
  }
  set cacheTime(t) {
    this.config.cacheTime = t;
    this.storeNeedsRecalc = true;
  }
  /** @inheritDoc */
  clone(config) {
    const inst = new _NgForageCache(this.baseConfig, this.fact);
    inst.configure(__spreadValues(__spreadValues({}, this.finalConfig), config));
    return inst;
  }
  /**
   * Retrieve data
   * @param key Data key
   */
  getCached(key) {
    return __async(this, null, function* () {
      const keys = calculateCacheKeys(key);
      const [data, expiry] = yield Promise.all([this.getItem(keys.data), this.getItem(keys.expiry)]);
      return new CachedItemImpl(data, expiry);
    });
  }
  /**
   * Remove data
   * @param key Data key
   */
  removeCached(key) {
    return __async(this, null, function* () {
      const keys = calculateCacheKeys(key);
      yield Promise.all([this.removeItem(keys.data), this.removeItem(keys.expiry)]);
    });
  }
  /**
   * Set data
   * @param key Data key
   * @param data Data to set
   * @param [cacheTime] Override cache set in {@link CacheConfigurable#cacheTime global or instance config}.
   */
  setCached(_0, _1) {
    return __async(this, arguments, function* (key, data, cacheTime = this.cacheTime) {
      const keys = calculateCacheKeys(key);
      const [out] = yield Promise.all([this.setItem(keys.data, data), this.setItem(keys.expiry, Date.now() + cacheTime)]);
      return out;
    });
  }
  /** @internal */
  toJSON() {
    return Object.assign(super.toJSON(), { cacheTime: this.cacheTime });
  }
};
NgForageCache.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForageCache, deps: null, target: FactoryTarget.Injectable });
NgForageCache.\u0275prov = \u0275\u0275ngDeclareInjectable({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForageCache, providedIn: "root" });
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: NgForageCache, decorators: [{
  type: Injectable,
  args: [{ providedIn: "root" }]
}] });
var NgForageCacheDedicated = class _NgForageCacheDedicated extends NgForageCache {
  /** @inheritDoc */
  clone(config) {
    const inst = new _NgForageCacheDedicated(this.baseConfig, this.fact);
    inst.configure(__spreadValues(__spreadValues({}, this.finalConfig), config));
    return inst;
  }
};
var NgForageDedicated = class _NgForageDedicated extends NgForage {
  /** @inheritDoc */
  clone(config) {
    const inst = new _NgForageDedicated(this.baseConfig, this.fact);
    inst.configure(__spreadValues(__spreadValues({}, this.finalConfig), config));
    return inst;
  }
};
var conf$ = Symbol("NgForageConfig");
var if$ = Symbol("InstanceFactory");
var DedicatedInstanceFactory = class {
  constructor(conf, instFact) {
    this[conf$] = conf;
    this[if$] = instFact;
  }
  createCache(config) {
    const inst = new NgForageCacheDedicated(this[conf$], this[if$]);
    if (config) {
      inst.configure(config);
    }
    return inst;
  }
  createNgForage(config) {
    const inst = new NgForageDedicated(this[conf$], this[if$]);
    if (config) {
      inst.configure(config);
    }
    return inst;
  }
};
DedicatedInstanceFactory.\u0275fac = \u0275\u0275ngDeclareFactory({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: DedicatedInstanceFactory, deps: [{ token: NgForageConfig }, { token: InstanceFactory }], target: FactoryTarget.Injectable });
DedicatedInstanceFactory.\u0275prov = \u0275\u0275ngDeclareInjectable({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: DedicatedInstanceFactory, providedIn: "root" });
\u0275\u0275ngDeclareClassMetadata({ minVersion: "12.0.0", version: "15.1.2", ngImport: core_exports, type: DedicatedInstanceFactory, decorators: [{
  type: Injectable,
  args: [{ providedIn: "root" }]
}], ctorParameters: function() {
  return [{ type: NgForageConfig }, { type: InstanceFactory }];
} });

// projects/aimmo-services/ngforage/src/rx-ngforage.ts
var _a2;
var RxNgForage = (_a2 = class {
  constructor(ngf) {
    this.ngf = ngf;
  }
  // 구현체 정의
  getItem(key, defaultValue) {
    return defer(() => this.ngf.getItem(key)).pipe(map((item) => item === null ? defaultValue : item));
  }
  setItem(key, data) {
    return defer(() => this.ngf.setItem(key, data));
  }
  removeItem(key) {
    return defer(() => this.ngf.removeItem(key));
  }
  keys() {
    return defer(() => this.ngf.keys());
  }
  hasItem(key) {
    return this.getItem(key).pipe(map((item) => !!item));
  }
}, _a2.ctorParameters = () => [
  { type: NgForage }
], _a2);
RxNgForage = __decorate([
  Injectable({ providedIn: "root" })
], RxNgForage);

// projects/aimmo-services/ngforage/src/rx-ngforage-cache.ts
var _a3;
var RxNgForageCache = (_a3 = class {
  constructor(ngfc) {
    this.ngfc = ngfc;
  }
  getCached(key) {
    return defer(() => this.ngfc.getCached(key));
  }
  setCached(key, data, cacheTime) {
    return defer(() => this.ngfc.setCached(key, data, cacheTime));
  }
  removeCached(key) {
    return defer(() => this.ngfc.removeCached(key));
  }
}, _a3.ctorParameters = () => [
  { type: NgForageCache }
], _a3);
RxNgForageCache = __decorate([
  Injectable({
    providedIn: "root"
  })
], RxNgForageCache);

// projects/aimmo-i18n/src/i18n-guard.service.ts
var LANGUAGE_QUERY_PARAM = "lang";
var DEFAULT_LANGUAGE = Lang.EN;
var _a4;
var I18nGuard = (_a4 = class {
  constructor(config, translate, rxNgForage) {
    this.config = config;
    this.translate = translate;
    this.rxNgForage = rxNgForage;
    this.initialized = false;
    this.translate.addLangs(this.config.supportLanguages);
    this.translate.setDefaultLang(DEFAULT_LANGUAGE);
  }
  canActivate(route2, state2) {
    return defer(() => {
      if (route2.queryParamMap.has(LANGUAGE_QUERY_PARAM)) {
        const lang = route2.queryParamMap.get(LANGUAGE_QUERY_PARAM);
        const languageCode2 = getLanguageCode(lang);
        if (languageCode2 && this.config.supportLanguages.includes(languageCode2)) {
          this.initialized = true;
          return this.setLanguage(lang);
        }
      }
      return this.initialSetLanguage();
    }).pipe(map(() => true));
  }
  setLanguage(lang) {
    return defer(() => {
      const languageCode2 = getLanguageCode(lang);
      if (languageCode2 && this.config.supportLanguages.includes(languageCode2)) {
        return this.translate.use(lang).pipe(switchMap(() => this.rxNgForage.setItem(this.config.savedLanguageKey, lang)), catchError(() => of(void 0)));
      }
      return of(void 0);
    });
  }
  initialSetLanguage() {
    return defer(() => {
      if (this.initialized) {
        return of(true);
      }
      this.initialized = true;
      return this.rxNgForage.getItem(this.config.savedLanguageKey).pipe(switchMap((savedLang) => {
        if (savedLang) {
          const languageCode2 = getLanguageCode(savedLang);
          if (languageCode2 && this.config.supportLanguages.includes(languageCode2)) {
            return this.translate.use(savedLang);
          }
        }
        let browserLang = this.translate.getBrowserLang();
        if (!this.config.supportLanguages.includes(browserLang)) {
          browserLang = DEFAULT_LANGUAGE;
        }
        return this.translate.use(browserLang);
      }));
    });
  }
}, _a4.ctorParameters = () => [
  { type: void 0, decorators: [{ type: Inject, args: [I18N_GUARD_CONFIG] }] },
  { type: TranslateService },
  { type: RxNgForage }
], _a4);
I18nGuard = __decorate([
  Injectable({
    providedIn: "root"
  })
], I18nGuard);

export {
  AimSelectModule,
  Lang,
  route
};
/*! Bundled license information:

localforage/dist/localforage.js:
  (*!
      localForage -- Offline Storage, Improved
      Version 1.10.0
      https://localforage.github.io/localForage
      (c) 2013-2017 Mozilla, Apache License 2.0
  *)
*/
