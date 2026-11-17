(function (window, document) {
  "use strict";

  var REF_ATTRIBUTE = "data-slide-ref";
  var TOKEN_IDREF_ATTRIBUTES = [
    "aria-describedby",
    "aria-labelledby",
    "aria-controls",
    "aria-owns",
    "aria-flowto",
    "headers",
    "for",
    "itemref"
  ];
  var LOCAL_REFERENCE_ATTRIBUTES = [
    "href",
    "xlink:href",
    "data-target",
    "data-bs-target",
    "data-slide-target",
    "data-controls",
    "data-describedby",
    "data-labelledby"
  ];

  function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
  }

  function isSection(element) {
    return element && element.nodeType === 1 && element.tagName.toLowerCase() === "section";
  }

  function isRevealSlide(element) {
    return isSection(element) && Boolean(element.closest(".reveal .slides"));
  }

  function reportError(alias, target, message) {
    var aliasId = alias && alias.getAttribute("id");
    var targetLabel = target || "(empty)";
    console.error(
      "[IE Slide Aliases] " + message +
      " Alias #" + (aliasId || "(missing id)") +
      " target #" + targetLabel
    );
  }

  function encodeIdPart(value) {
    var encoded = "";
    var index;

    for (index = 0; index < value.length; index += 1) {
      var code = value.charCodeAt(index);
      var character = value.charAt(index);
      var isLetter = (code >= 65 && code <= 90) || (code >= 97 && code <= 122);
      var isNumber = code >= 48 && code <= 57;

      if (isLetter || isNumber || character === "_" || character === "-") {
        encoded += character;
      } else {
        encoded += "_x" + code.toString(16) + "_";
      }
    }

    return encoded || "empty";
  }

  function namespacedId(aliasId, sourceId) {
    var aliasPart = encodeIdPart(aliasId);
    if (/^[0-9]/.test(aliasPart)) aliasPart = "_" + aliasPart;
    return aliasPart + "__" + encodeIdPart(sourceId);
  }

  function copySlideAttributes(alias, source) {
    Array.prototype.slice.call(alias.attributes).forEach(function (attribute) {
      if (attribute.name !== "id" && attribute.name !== REF_ATTRIBUTE) {
        alias.removeAttribute(attribute.name);
      }
    });

    Array.prototype.forEach.call(source.attributes, function (attribute) {
      if (attribute.name !== "id" && attribute.name !== REF_ATTRIBUTE) {
        alias.setAttribute(attribute.name, attribute.value);
      }
    });
  }

  function buildIdMap(alias, source, sourceClone) {
    var idMap = Object.create(null);
    var usedIds = Object.create(null);
    var aliasId = alias.getAttribute("id");
    var sourceId = source.getAttribute("id");

    if (sourceId) {
      idMap[sourceId] = aliasId;
    }

    Array.prototype.forEach.call(sourceClone.querySelectorAll("[id]"), function (element) {
      var originalId = element.getAttribute("id");
      var baseId = namespacedId(aliasId, originalId);
      var nextId = baseId;
      var suffix = 1;

      while (usedIds[nextId] || document.getElementById(nextId)) {
        suffix += 1;
        nextId = baseId + "__" + suffix;
      }

      usedIds[nextId] = true;
      if (!hasOwn(idMap, originalId)) {
        idMap[originalId] = nextId;
      } else {
        console.warn(
          "[IE Slide Aliases] Duplicate descendant id #" + originalId +
          " in canonical slide #" + sourceId +
          " while materializing alias #" + aliasId
        );
      }
      element.setAttribute("id", nextId);
    });

    return idMap;
  }

  function rewriteTokens(value, idMap) {
    return value.trim().split(/\s+/).map(function (token) {
      return hasOwn(idMap, token) ? idMap[token] : token;
    }).join(" ");
  }

  function rewriteLocalReferences(value, idMap) {
    var updated = value;

    if (updated.charAt(0) === "#") {
      var directId = updated.slice(1);
      if (hasOwn(idMap, directId)) return "#" + idMap[directId];
    }

    return updated.replace(/(^|url\()#([^)#\s]+)/g, function (match, prefix, referencedId) {
      return hasOwn(idMap, referencedId) ? prefix + "#" + idMap[referencedId] : match;
    });
  }

  function rewriteCssIdSelectors(cssText, idMap) {
    var updated = cssText;

    Object.keys(idMap).forEach(function (originalId) {
      var escapedId = originalId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      updated = updated.replace(
        new RegExp("#" + escapedId + "(?![A-Za-z0-9_-])", "g"),
        "#" + idMap[originalId]
      );
    });

    return updated;
  }

  function rewriteElementReferences(element, idMap) {
    Array.prototype.forEach.call(element.attributes, function (attribute) {
      var attributeName = attribute.name.toLowerCase();
      var value = attribute.value;
      var updated = value;

      if (TOKEN_IDREF_ATTRIBUTES.indexOf(attributeName) !== -1) {
        updated = rewriteTokens(value, idMap);
      } else if (
        LOCAL_REFERENCE_ATTRIBUTES.indexOf(attributeName) !== -1 ||
        attributeName === "style" ||
        value.indexOf("url(#") !== -1
      ) {
        updated = rewriteLocalReferences(value, idMap);
      }

      if (updated !== value) element.setAttribute(attribute.name, updated);
    });
  }

  function rewriteReferences(alias, idMap) {
    rewriteElementReferences(alias, idMap);
    Array.prototype.forEach.call(alias.querySelectorAll("*"), function (element) {
      rewriteElementReferences(element, idMap);
    });
    Array.prototype.forEach.call(alias.querySelectorAll("style"), function (styleElement) {
      styleElement.textContent = rewriteCssIdSelectors(styleElement.textContent, idMap);
    });
  }

  function hasUniqueId(element) {
    var elementId = element.getAttribute("id");
    var matches = Array.prototype.filter.call(document.querySelectorAll("[id]"), function (candidate) {
      return candidate.getAttribute("id") === elementId;
    });
    return Boolean(elementId) && matches.length === 1 && matches[0] === element;
  }

  function hasCircularAliasReference(startId) {
    var seen = Object.create(null);
    var currentId = startId;

    while (currentId) {
      if (hasOwn(seen, currentId)) return true;
      seen[currentId] = true;
      var candidate = document.getElementById(currentId);
      if (!candidate || !candidate.hasAttribute(REF_ATTRIBUTE)) return false;
      currentId = candidate.getAttribute(REF_ATTRIBUTE);
    }

    return false;
  }

  function materializeAlias(alias) {
    var targetId = alias.getAttribute(REF_ATTRIBUTE);
    var source = targetId ? document.getElementById(targetId) : null;

    if (!isRevealSlide(alias)) {
      reportError(alias, targetId, "Alias must be a section inside the Reveal slides container");
      return false;
    }
    if (!hasUniqueId(alias)) {
      reportError(alias, targetId, "Alias must have a unique top-level id");
      return false;
    }
    if (!source || !isRevealSlide(source)) {
      reportError(alias, targetId, "Canonical slide was not found");
      return false;
    }
    if (source === alias) {
      reportError(alias, targetId, "Alias cannot reference itself");
      return false;
    }
    if (source.hasAttribute(REF_ATTRIBUTE)) {
      var chainMessage = hasCircularAliasReference(targetId)
        ? "Circular alias reference detected"
        : "Alias targets another alias; references must point directly to canonical slides";
      reportError(alias, targetId, chainMessage);
      return false;
    }
    if (alias.contains(source)) {
      reportError(alias, targetId, "Alias cannot contain its canonical source");
      return false;
    }

    var sourceClone = source.cloneNode(true);
    alias.replaceChildren();
    copySlideAttributes(alias, source);
    var idMap = buildIdMap(alias, source, sourceClone);

    while (sourceClone.firstChild) {
      alias.appendChild(sourceClone.firstChild);
    }
    rewriteReferences(alias, idMap);
    alias.__ieSlideAliasResolved = true;
    return true;
  }

  function resolveAliases() {
    var materialized = 0;

    Array.prototype.forEach.call(
      document.querySelectorAll("section[" + REF_ATTRIBUTE + "]"),
      function (alias) {
        if (alias.__ieSlideAliasResolved) return;
        if (materializeAlias(alias)) materialized += 1;
      }
    );

    return materialized;
  }

  window.IESlideAliases = {
    resolve: resolveAliases
  };
}(window, document));
